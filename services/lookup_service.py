#!/usr/bin/env python3
"""
OpenClaw Dynamic Skills — Lookup Service (Phase 1)

FastAPI service for skill lookup and retrieval.

Usage:
    python3 lookup_service.py

Environment Variables:
    SKILLS_DB_DSN: PostgreSQL connection string (required)
    SKILLS_LOOKUP_PORT: Port to listen on (default: 8845)
    SKILLS_REDIS_ENABLED: Enable Redis caching (default: false)
    SKILLS_REDIS_HOST: Redis host (default: localhost)
    SKILLS_REDIS_PORT: Redis port (default: 6379)
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

# Try to import dependencies
try:
    from fastapi import FastAPI, HTTPException, Header
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("❌ FastAPI not installed. Install with: pip3 install fastapi uvicorn")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("❌ psycopg2 not installed. Install with: pip3 install psycopg2-binary")
    sys.exit(1)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    UVICORN_AVAILABLE = False
    print("❌ uvicorn not installed. Install with: pip3 install uvicorn")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

DB_DSN = os.getenv('SKILLS_DB_DSN', 'postgresql://localhost:5432/skillsdb')
PORT = int(os.getenv('SKILLS_LOOKUP_PORT', '8845'))
REDIS_ENABLED = os.getenv('SKILLS_REDIS_ENABLED', 'false').lower() == 'true'
REDIS_HOST = os.getenv('SKILLS_REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('SKILLS_REDIS_PORT', '6379'))
API_KEY = os.getenv('SKILLS_LOOKUP_API_KEY', '')  # Optional authentication

# Redis client (initialized if enabled)
redis_client = None
if REDIS_ENABLED and REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)
        redis_client.ping()
        print(f"✅ Redis connected at {REDIS_HOST}:{REDIS_PORT}")
    except Exception as e:
        print(f"⚠️  Redis connection failed: {e}. Disabling cache.")
        redis_client = None


# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class LookupRequest(BaseModel):
    query: str
    task_summary: Optional[str] = None
    max_skills: int = 2
    agent_name: Optional[str] = None  # 'arty' or 'brodie'


class SkillResult(BaseModel):
    id: str
    name: str
    description: str
    version: int
    excerpt: str
    risk_level: int
    tags: List[str]


class LookupResponse(BaseModel):
    skills: List[SkillResult]
    query: str
    count: int


# ============================================================================
# DATABASE
# ============================================================================

def get_db_connection():
    """Get PostgreSQL connection."""
    return psycopg2.connect(DB_DSN)


def keyword_search(query: str, max_skills: int = 2, agent_name: Optional[str] = None) -> List[Dict]:
    """
    Search skills by keyword matching.
    
    Searches in: name, description, tags, body
    """
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Build search query
    search_terms = query.lower().split()
    conditions = []
    params = []
    
    for term in search_terms:
        if len(term) < 3:
            continue
        
        conditions.append("""
            (name ILIKE %s OR 
             description ILIKE %s OR 
             body ILIKE %s OR
             tags::text ILIKE %s)
        """)
        like_term = f"%{term}%"
        params.extend([like_term, like_term, like_term, like_term])
    
    if not conditions:
        cur.close()
        conn.close()
        return []
    
    # Add agent allowlist filter
    if agent_name:
        conditions.append("(agent_allowlist = '{}' OR %s = ANY(agent_allowlist))")
        params.append(agent_name)
    
    # Build final query
    where_clause = " AND ".join(conditions)
    sql = f"""
        SELECT id, name, description, version, body, risk_level, tags
        FROM skills
        WHERE status = 'active' AND ({where_clause})
        ORDER BY 
            CASE WHEN name ILIKE %s THEN 0 ELSE 1 END,
            execution_count DESC,
            updated_at DESC
        LIMIT %s
    """
    
    params.extend([f"%{query}%", max_skills])
    
    cur.execute(sql, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    
    return results


def get_skill_by_id(skill_id: str) -> Optional[Dict]:
    """Get full skill by ID."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT * FROM skills
        WHERE id = %s AND status = 'active'
    """, (skill_id,))
    
    result = cur.fetchone()
    cur.close()
    conn.close()
    
    return result


def log_usage(skill_id: str, agent_name: str, query: str, 
              executed: bool = False, result: Optional[str] = None, 
              duration_ms: Optional[int] = None, error: Optional[str] = None):
    """Log skill usage for analytics."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Generate XID-like ID (simple fallback)
        log_id = f"01{datetime.now().strftime('%y%m%d%H%M%S')}{hashlib.md5(f'{skill_id}{datetime.now()}'.encode()).hexdigest()[:14]}"
        
        cur.execute("""
            INSERT INTO skill_usage_logs 
            (id, skill_id, agent_name, query, executed, execution_result, duration_ms, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (log_id, skill_id, agent_name, query, executed, result, duration_ms, error))
        
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"⚠️  Failed to log usage: {e}")


# ============================================================================
# CACHING
# ============================================================================

def cache_key(query: str, max_skills: int, agent_name: Optional[str] = None) -> str:
    """Generate cache key for query."""
    key_str = f"{query}:{max_skills}:{agent_name or 'all'}"
    return f"skills:lookup:{hashlib.md5(key_str.encode()).hexdigest()}"


def get_from_cache(key: str) -> Optional[List[Dict]]:
    """Get results from Redis cache."""
    if not redis_client:
        return None
    
    try:
        cached = redis_client.get(key)
        if cached:
            return json.loads(cached)
    except Exception as e:
        print(f"⚠️  Cache get error: {e}")
    
    return None


def set_in_cache(key: str, value: List[Dict], ttl: int = 300):
    """Set results in Redis cache (5 minute TTL)."""
    if not redis_client:
        return
    
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except Exception as e:
        print(f"⚠️  Cache set error: {e}")


# ============================================================================
# FASTAPI APP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    print(f"🚀 Skills Lookup Service starting on port {PORT}")
    print(f"   Database: {'✅' if PSYCOPG2_AVAILABLE else '❌'}")
    print(f"   Redis Cache: {'✅' if redis_client else '⚠️  Disabled'}")
    print(f"   API Key: {'✅ Set' if API_KEY else '⚠️  Not set'}")
    yield
    print("👋 Skills Lookup Service shutting down")


app = FastAPI(
    title="OpenClaw Dynamic Skills Lookup",
    description="Semantic and keyword search for OpenClaw skills",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================================
# ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "service": "OpenClaw Dynamic Skills Lookup",
        "version": "1.0.0",
        "status": "running",
        "redis_enabled": redis_client is not None
    }


@app.get("/health")
async def health():
    """Detailed health check."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM skills WHERE status = 'active'")
        skill_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "active_skills": skill_count,
            "redis": "connected" if redis_client else "disabled"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database error: {e}")


@app.post("/skills/lookup", response_model=LookupResponse)
async def lookup_skills(
    request: LookupRequest,
    x_api_key: Optional[str] = Header(None)
):
    """
    Search for relevant skills based on query.
    
    - **query**: Search terms (required)
    - **task_summary**: Optional task context
    - **max_skills**: Maximum results (default: 2)
    - **agent_name**: Agent making request (for allowlist filtering)
    """
    # Optional API key validation
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check cache
    cache_k = cache_key(request.query, request.max_skills, request.agent_name)
    cached = get_from_cache(cache_k)
    
    if cached:
        return LookupResponse(
            skills=[SkillResult(**s) for s in cached],
            query=request.query,
            count=len(cached)
        )
    
    # Database search
    try:
        results = keyword_search(
            request.query,
            max_skills=request.max_skills,
            agent_name=request.agent_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {e}")
    
    # Format results
    formatted_results = []
    for skill in results:
        # Create excerpt (first 200 chars of body)
        excerpt = skill['body'][:200] + "..." if len(skill['body']) > 200 else skill['body']
        
        formatted_results.append({
            'id': skill['id'],
            'name': skill['name'],
            'description': skill['description'] or '',
            'version': skill['version'],
            'excerpt': excerpt,
            'risk_level': skill['risk_level'],
            'tags': skill['tags'] or []
        })
    
    # Cache results
    set_in_cache(cache_k, formatted_results)
    
    # Log usage (async, non-blocking)
    if results:
        log_usage(
            skill_id=results[0]['id'],
            agent_name=request.agent_name or 'unknown',
            query=request.query
        )
    
    return LookupResponse(
        skills=[SkillResult(**s) for s in formatted_results],
        query=request.query,
        count=len(formatted_results)
    )


@app.get("/skills/{skill_id}")
async def get_skill(skill_id: str, x_api_key: Optional[str] = Header(None)):
    """Get full skill by ID."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    skill = get_skill_by_id(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return {
        'id': skill['id'],
        'name': skill['name'],
        'description': skill['description'],
        'body': skill['body'],
        'metadata': skill['metadata'],
        'version': skill['version'],
        'risk_level': skill['risk_level'],
        'tags': skill['tags']
    }


@app.get("/skills")
async def list_skills(
    status: str = 'active',
    limit: int = 50,
    x_api_key: Optional[str] = Header(None)
):
    """List all skills (optionally filtered by status)."""
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    cur.execute("""
        SELECT id, name, description, version, status, risk_level, tags, 
               execution_count, last_used_at, created_at
        FROM skills
        WHERE status = %s
        ORDER BY name
        LIMIT %s
    """, (status, limit))
    
    skills = cur.fetchall()
    cur.close()
    conn.close()
    
    return {
        'skills': skills,
        'count': len(skills),
        'status': status
    }


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the lookup service."""
    if not UVICORN_AVAILABLE:
        print("❌ uvicorn not installed")
        sys.exit(1)
    
    print(f"🚀 Starting Skills Lookup Service on port {PORT}")
    print(f"   Redis: {'Enabled' if redis_client else 'Disabled'}")
    print(f"   API Key: {'Set' if API_KEY else 'Not set'}")
    print("")
    
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == '__main__':
    main()
