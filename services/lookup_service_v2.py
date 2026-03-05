#!/usr/bin/env python3
"""
OpenClaw Dynamic Skills — Lookup Service (Phase 2)

FastAPI service with semantic + keyword hybrid search.

Usage:
    python3 lookup_service.py

Environment Variables:
    SKILLS_DB_DSN: PostgreSQL connection string
    SKILLS_LOOKUP_PORT: Port (default: 8845)
    SKILLS_REDIS_ENABLED: Enable Redis (default: false)
    SKILLS_LOOKUP_API_KEY: Optional API key
"""

import os
import sys
import json
import hashlib
from datetime import datetime
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager

try:
    from fastapi import FastAPI, HTTPException, Header
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    FASTAPI_AVAILABLE = True
except ImportError:
    print("❌ FastAPI not installed")
    sys.exit(1)

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    print("❌ psycopg2 not installed")
    sys.exit(1)

try:
    import redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
    MODEL = None
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    import uvicorn
    UVICORN_AVAILABLE = True
except ImportError:
    print("❌ uvicorn not installed")
    sys.exit(1)


# ============================================================================
# CONFIGURATION
# ============================================================================

DB_DSN = os.getenv('SKILLS_DB_DSN', 'postgresql://localhost:5432/skillsdb')
PORT = int(os.getenv('SKILLS_LOOKUP_PORT', '8845'))
REDIS_ENABLED = os.getenv('SKILLS_REDIS_ENABLED', 'false').lower() == 'true'
REDIS_HOST = os.getenv('SKILLS_REDIS_HOST', 'localhost')
REDIS_PORT = int(os.getenv('SKILLS_REDIS_PORT', '6379'))
API_KEY = os.getenv('SKILLS_LOOKUP_API_KEY', '')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')

# Redis client
redis_client = None
if REDIS_ENABLED and REDIS_AVAILABLE:
    try:
        redis_client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=1, decode_responses=True)
        redis_client.ping()
        print(f"✅ Redis connected")
    except Exception as e:
        print(f"⚠️  Redis failed: {e}")

# Load embedding model for semantic search
if SENTENCE_TRANSFORMERS_AVAILABLE:
    try:
        print(f"📥 Loading embedding model: {EMBEDDING_MODEL}")
        MODEL = SentenceTransformer(EMBEDDING_MODEL)
        print(f"✅ Model loaded (384 dimensions)")
    except Exception as e:
        print(f"⚠️  Model load failed: {e}")
        MODEL = None


# ============================================================================
# MODELS
# ============================================================================

class LookupRequest(BaseModel):
    query: str
    task_summary: Optional[str] = None
    max_skills: int = 2
    agent_name: Optional[str] = None
    search_type: str = 'hybrid'  # keyword, semantic, hybrid


class SkillResult(BaseModel):
    id: str
    name: str
    description: str
    version: int
    excerpt: str
    risk_level: int
    tags: List[str]
    similarity_score: Optional[float] = None


class LookupResponse(BaseModel):
    skills: List[SkillResult]
    query: str
    count: int
    search_type: str


# ============================================================================
# DATABASE
# ============================================================================

def get_db_connection():
    return psycopg2.connect(DB_DSN)


def keyword_search(query: str, max_skills: int = 2, agent_name: Optional[str] = None) -> List[Dict]:
    """Keyword search across name, description, tags, body."""
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    search_terms = query.lower().split()
    conditions = []
    params = []
    
    for term in search_terms:
        if len(term) < 3:
            continue
        conditions.append("(name ILIKE %s OR description ILIKE %s OR body ILIKE %s OR tags::text ILIKE %s)")
        like_term = f"%{term}%"
        params.extend([like_term, like_term, like_term, like_term])
    
    if not conditions:
        cur.close()
        conn.close()
        return []
    
    if agent_name:
        conditions.append("(agent_allowlist = '{}' OR %s = ANY(agent_allowlist))")
        params.append(agent_name)
    
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


def semantic_search(query: str, max_skills: int = 2, agent_name: Optional[str] = None) -> List[Dict]:
    """Semantic search using pgvector cosine similarity."""
    if MODEL is None:
        return keyword_search(query, max_skills, agent_name)
    
    # Generate query embedding
    query_embedding = MODEL.encode(query, convert_to_numpy=True).tolist()
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Agent filter
    agent_filter = ""
    if agent_name:
        agent_filter = "AND (agent_allowlist = '{}' OR %s = ANY(agent_allowlist))"
    
    # Cosine similarity search
    sql = f"""
        SELECT id, name, description, version, body, risk_level, tags,
               1 - (embedding <=> %s::vector(384)) as similarity_score
        FROM skills
        WHERE status = 'active' AND embedding IS NOT NULL
        {agent_filter}
        ORDER BY similarity_score DESC
        LIMIT %s
    """
    
    params = [query_embedding]
    if agent_name:
        params.append(agent_name)
    params.append(max_skills)
    
    cur.execute(sql, params)
    results = cur.fetchall()
    cur.close()
    conn.close()
    return results


def hybrid_search(query: str, max_skills: int = 2, agent_name: Optional[str] = None) -> List[Dict]:
    """Hybrid search: combines keyword + semantic results."""
    keyword_results = keyword_search(query, max_skills * 2, agent_name)
    semantic_results = semantic_search(query, max_skills * 2, agent_name)
    
    # Merge and deduplicate by skill id
    seen_ids = set()
    merged = []
    
    # Add semantic results first (usually more relevant)
    for skill in semantic_results:
        if skill['id'] not in seen_ids:
            seen_ids.add(skill['id'])
            merged.append({
                **skill,
                'search_type': 'semantic',
                'similarity_score': float(skill.get('similarity_score', 0))
            })
    
    # Add keyword results
    for skill in keyword_results:
        if skill['id'] not in seen_ids:
            seen_ids.add(skill['id'])
            merged.append({
                **skill,
                'search_type': 'keyword',
                'similarity_score': 0.0
            })
    
    return merged[:max_skills]


def log_usage(skill_id: str, agent_name: str, query: str, 
              executed: bool = False, result: Optional[str] = None,
              duration_ms: Optional[int] = None, error: Optional[str] = None):
    """Log skill usage."""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
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
        print(f"⚠️  Log failed: {e}")


# ============================================================================
# CACHING
# ============================================================================

def cache_key(query: str, max_skills: int, search_type: str, agent_name: Optional[str] = None) -> str:
    return f"skills:{search_type}:{query}:{max_skills}:{agent_name or 'all'}"


def get_from_cache(key: str) -> Optional[List[Dict]]:
    if not redis_client:
        return None
    try:
        cached = redis_client.get(key)
        return json.loads(cached) if cached else None
    except:
        return None


def set_in_cache(key: str, value: List[Dict], ttl: int = 300):
    if not redis_client:
        return
    try:
        redis_client.setex(key, ttl, json.dumps(value))
    except:
        pass


# ============================================================================
# FASTAPI APP
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"🚀 Skills Lookup Service v2.0 (Phase 2)")
    print(f"   Port: {PORT}")
    print(f"   Search: Keyword + Semantic + Hybrid")
    print(f"   Redis: {'✅' if redis_client else '⚠️  Disabled'}")
    print(f"   Embeddings: {'✅' if MODEL else '❌'}")
    yield
    print("👋 Shutting down")


app = FastAPI(title="OpenClaw Dynamic Skills Lookup v2", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"service": "OpenClaw Dynamic Skills Lookup v2", "version": "2.0.0", "status": "running"}


@app.get("/health")
async def health():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM skills WHERE status = 'active'")
        skill_count = cur.fetchone()[0]
        cur.execute("SELECT COUNT(*) FROM skills WHERE embedding IS NOT NULL")
        embedded_count = cur.fetchone()[0]
        cur.close()
        conn.close()
        
        return {
            "status": "healthy",
            "database": "connected",
            "active_skills": skill_count,
            "skills_with_embeddings": embedded_count,
            "redis": "connected" if redis_client else "disabled",
            "semantic_search": "enabled" if MODEL else "disabled"
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))


@app.post("/skills/lookup", response_model=LookupResponse)
async def lookup_skills(request: LookupRequest, x_api_key: Optional[str] = Header(None)):
    """
    Search for skills (Phase 2: Hybrid search)
    
    - search_type: 'keyword', 'semantic', or 'hybrid' (default)
    """
    if API_KEY and x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Check cache
    cache_k = cache_key(request.query, request.max_skills, request.search_type, request.agent_name)
    cached = get_from_cache(cache_k)
    
    if cached:
        return LookupResponse(
            skills=[SkillResult(**s) for s in cached],
            query=request.query,
            count=len(cached),
            search_type=request.search_type
        )
    
    # Perform search
    if request.search_type == 'keyword':
        results = keyword_search(request.query, request.max_skills, request.agent_name)
    elif request.search_type == 'semantic':
        results = semantic_search(request.query, request.max_skills, request.agent_name)
    else:  # hybrid
        results = hybrid_search(request.query, request.max_skills, request.agent_name)
    
    # Format results
    formatted = []
    for skill in results:
        excerpt = skill['body'][:200] + "..." if len(skill['body']) > 200 else skill['body']
        formatted.append({
            'id': skill['id'],
            'name': skill['name'],
            'description': skill.get('description', ''),
            'version': skill['version'],
            'excerpt': excerpt,
            'risk_level': skill.get('risk_level', 1),
            'tags': skill.get('tags', []),
            'similarity_score': skill.get('similarity_score')
        })
    
    # Cache
    set_in_cache(cache_k, formatted)
    
    # Log usage
    if results:
        log_usage(results[0]['id'], request.agent_name or 'unknown', request.query)
    
    return LookupResponse(
        skills=[SkillResult(**s) for s in formatted],
        query=request.query,
        count=len(formatted),
        search_type=request.search_type
    )


@app.get("/skills/{skill_id}")
async def get_skill(skill_id: str):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT * FROM skills WHERE id = %s AND status = 'active'", (skill_id,))
    skill = cur.fetchone()
    cur.close()
    conn.close()
    
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    
    return skill


@app.get("/skills")
async def list_skills(status: str = 'active', limit: int = 50):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT id, name, description, version, status, risk_level, tags,
               execution_count, last_used_at, created_at
        FROM skills WHERE status = %s ORDER BY name LIMIT %s
    """, (status, limit))
    skills = cur.fetchall()
    cur.close()
    conn.close()
    return {'skills': skills, 'count': len(skills)}


def main():
    if not UVICORN_AVAILABLE:
        print("❌ uvicorn not installed")
        sys.exit(1)
    
    print(f"🚀 Starting Skills Lookup Service v2.0 on port {PORT}")
    print(f"   Semantic Search: {'✅' if MODEL else '❌'}")
    print(f"   Redis Cache: {'✅' if redis_client else 'Disabled'}")
    uvicorn.run(app, host="0.0.0.0", port=PORT)


if __name__ == '__main__':
    main()
