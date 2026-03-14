#!/usr/bin/env python3
"""
OpenClaw Dynamic Skills — Import Tool (Phase 1)

Imports skills from Anthropic skills repository via GitHub URL.

Usage:
    python3 import_skill.py <github-url>
    
Examples:
    python3 import_skill.py https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md
    python3 import_skill.py https://raw.githubusercontent.com/anthropics/skills/main/skills/webapp-testing/SKILL.md

Environment Variables:
    SKILLS_DB_DSN: PostgreSQL connection string (required)
    SKILLS_REDIS_ENABLED: Enable Redis caching (optional, default: false)
"""

import os
import sys
import re
import json
import hashlib
import argparse
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, Tuple
from urllib.parse import urlparse

# Try to import optional dependencies
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️  Warning: 'requests' library not installed. Install with: pip3 install requests")

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False
    print("⚠️  Warning: 'psycopg2' library not installed. Install with: pip3 install psycopg2-binary")

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("⚠️  Warning: 'pyyaml' library not installed. Install with: pip3 install pyyaml")

try:
    # Try to import xid for compact IDs
    from xid import Xid
    XID_AVAILABLE = True
except ImportError:
    XID_AVAILABLE = False
    print("⚠️  Warning: 'xid' library not installed. Using UUID fallback. Install with: pip3 install xid")
    import uuid


# ============================================================================
# ID GENERATION
# ============================================================================

def generate_id() -> str:
    """Generate a compact, time-sorted ID using XID (preferred) or UUID (fallback)."""
    if XID_AVAILABLE:
        return str(Xid().string())
    return str(uuid.uuid4())


# ============================================================================
# URL PARSING
# ============================================================================

def parse_github_url(url: str) -> Tuple[str, str]:
    """
    Parse GitHub URL and return (owner/repo, path).
    
    Supports:
    - https://github.com/owner/repo/blob/main/path/to/file.md
    - https://raw.githubusercontent.com/owner/repo/main/path/to/file.md
    """
    # GitHub blob URL
    blob_pattern = r'github\.com/([^/]+/[^/]+)/blob/[^/]+/(.+)'
    match = re.search(blob_pattern, url)
    if match:
        return match.group(1), match.group(2)
    
    # Raw GitHub URL
    raw_pattern = r'raw\.githubusercontent\.com/([^/]+/[^/]+)/[^/]+/(.+)'
    match = re.search(raw_pattern, url)
    if match:
        return match.group(1), match.group(2)
    
    raise ValueError(f"Invalid GitHub URL format: {url}")


def get_raw_url(url: str) -> str:
    """Convert GitHub URL to raw content URL."""
    owner_repo, path = parse_github_url(url)
    return f"https://raw.githubusercontent.com/{owner_repo}/main/{path}"


# ============================================================================
# SKILL PARSING
# ============================================================================

def parse_skill_markdown(content: str) -> Dict[str, Any]:
    """
    Parse SKILL.md content with YAML frontmatter.
    
    Returns dict with:
    - metadata: dict from YAML frontmatter
    - body: markdown content after frontmatter
    """
    if not YAML_AVAILABLE:
        # Fallback: simple regex parsing
        return parse_skill_simple(content)
    
    # Split frontmatter and body
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            frontmatter_str = parts[1].strip()
            body = parts[2].strip()
            
            try:
                metadata = yaml.safe_load(frontmatter_str) or {}
                return {
                    'metadata': metadata,
                    'body': body
                }
            except yaml.YAMLError as e:
                raise ValueError(f"Invalid YAML frontmatter: {e}")
    
    # No frontmatter
    return {
        'metadata': {},
        'body': content
    }


def parse_skill_simple(content: str) -> Dict[str, Any]:
    """Simple fallback parser when pyyaml is not available."""
    lines = content.split('\n')
    metadata = {}
    body_lines = []
    in_frontmatter = False
    
    for i, line in enumerate(lines):
        if line.strip() == '---':
            if not in_frontmatter:
                in_frontmatter = True
            else:
                # End of frontmatter
                body_lines = lines[i+1:]
                break
        elif in_frontmatter:
            # Parse key: value
            if ':' in line:
                key, value = line.split(':', 1)
                metadata[key.strip()] = value.strip()
    
    if not body_lines:
        body_lines = lines
    
    return {
        'metadata': metadata,
        'body': '\n'.join(body_lines).strip()
    }


def normalize_metadata(metadata: Dict[str, Any], source_url: str) -> Dict[str, Any]:
    """
    Normalize skill metadata to OpenClaw format.
    
    Adds:
    - source information
    - risk_level (default: 1)
    - tags (extracted from name/description)
    - reinforcement preference (default: preferred)
    """
    normalized = {
        'name': metadata.get('name', 'unknown'),
        'description': metadata.get('description', ''),
        'source': metadata.get('source', 'anthropics/skills'),
        'source_url': source_url,
        'user_invocable': metadata.get('user-invocable', True),
        'risk_level': 1,  # Default low risk
        'tags': [],
        'reinforcement': metadata.get('reinforcement', 'preferred')  # NEW: prompt reinforcement
    }
    
    # Extract tags from name
    name = normalized['name']
    if name:
        # Split on hyphens and underscores
        tags = re.split(r'[-_]', name)
        normalized['tags'] = [tag.lower() for tag in tags if len(tag) > 2]
    
    # Copy remaining metadata
    for key, value in metadata.items():
        if key not in ['name', 'description', 'user-invocable']:
            normalized[key] = value
    
    return normalized


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def get_db_connection():
    """Get PostgreSQL connection from environment variable."""
    dsn = os.getenv('SKILLS_DB_DSN')
    if not dsn:
        raise RuntimeError(
            "SKILLS_DB_DSN environment variable not set.\n"
            "Example: export SKILLS_DB_DSN='postgresql://user:pass@localhost:5432/skillsdb'"
        )
    
    return psycopg2.connect(dsn)


def calculate_body_hash(body: str) -> str:
    """Calculate SHA256 hash of skill body for deduplication."""
    return hashlib.sha256(body.encode('utf-8')).hexdigest()


def skill_exists(conn, body_hash: str) -> Optional[Dict]:
    """Check if skill with same body_hash already exists."""
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        cur.execute("""
            SELECT id, name, version, status 
            FROM skills 
            WHERE body_hash = %s
        """, (body_hash,))
        return cur.fetchone()


def upsert_skill(conn, skill_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Insert or update skill in database.
    
    Returns dict with:
    - skill_id: UUID of inserted/updated skill
    - action: 'inserted' or 'updated'
    - version: skill version number
    """
    with conn.cursor(cursor_factory=RealDictCursor) as cur:
        # Check if skill exists (by name)
        cur.execute("""
            SELECT id, version, body_hash 
            FROM skills 
            WHERE name = %s
        """, (skill_data['name'],))
        existing = cur.fetchone()
        
        if existing:
            # Update existing skill
            if existing['body_hash'] == skill_data['body_hash']:
                # No changes
                return {
                    'skill_id': existing['id'],
                    'action': 'unchanged',
                    'version': existing['version'],
                    'message': 'Skill already exists with identical content'
                }
            
            # Content changed - increment version
            new_version = existing['version'] + 1
            cur.execute("""
                UPDATE skills SET
                    body = %s,
                    metadata = %s,
                    version = %s,
                    body_hash = %s,
                    status = 'active',
                    updated_at = NOW()
                WHERE id = %s
                RETURNING id
            """, (
                skill_data['body'],
                json.dumps(skill_data['metadata']),
                new_version,
                skill_data['body_hash'],
                existing['id']
            ))
            
            skill_id = cur.fetchone()['id']
            return {
                'skill_id': skill_id,
                'action': 'updated',
                'version': new_version,
                'message': f'Skill updated to version {new_version}'
            }
        
        else:
            # Insert new skill
            skill_id = generate_id()
            cur.execute("""
                INSERT INTO skills (
                    id, source, source_url, source_path, name, description,
                    body, metadata, tags, version, status, risk_level,
                    body_hash, agent_allowlist
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                skill_id,
                skill_data['metadata'].get('source', 'anthropics/skills'),
                skill_data['metadata']['source_url'],
                skill_data['metadata'].get('source_path'),
                skill_data['name'],
                skill_data['metadata'].get('description', ''),
                skill_data['body'],
                json.dumps(skill_data['metadata']),
                skill_data['metadata'].get('tags', []),
                1,  # version
                'active',
                skill_data['metadata'].get('risk_level', 1),
                skill_data['body_hash'],
                []  # agent_allowlist (empty = all agents)
            ))
            
            return {
                'skill_id': skill_id,
                'action': 'inserted',
                'version': 1,
                'message': 'New skill inserted'
            }


# ============================================================================
# MAIN IMPORT FUNCTION
# ============================================================================

def import_skill(url: str, force: bool = False) -> Dict[str, Any]:
    """
    Import a skill from GitHub URL.
    
    Args:
        url: GitHub URL to SKILL.md
        force: Force re-import even if unchanged
    
    Returns:
        Dict with import results
    """
    if not REQUESTS_AVAILABLE:
        return {'ok': False, 'error': 'requests library not installed'}
    
    if not PSYCOPG2_AVAILABLE:
        return {'ok': False, 'error': 'psycopg2 library not installed'}
    
    # Parse URL
    try:
        raw_url = get_raw_url(url)
        owner_repo, path = parse_github_url(url)
    except Exception as e:
        return {'ok': False, 'error': f'Invalid URL: {e}'}
    
    # Fetch SKILL.md
    print(f"📥 Fetching {raw_url}...")
    try:
        response = requests.get(raw_url, timeout=30)
        response.raise_for_status()
        content = response.text
    except requests.RequestException as e:
        return {'ok': False, 'error': f'Failed to fetch: {e}'}
    
    # Parse skill
    print("📝 Parsing skill...")
    try:
        parsed = parse_skill_markdown(content)
        metadata = parsed['metadata']
        body = parsed['body']
    except Exception as e:
        return {'ok': False, 'error': f'Parse error: {e}'}
    
    # Normalize metadata
    metadata['source_url'] = url
    metadata['source_path'] = path
    normalized = normalize_metadata(metadata, url)
    
    # Calculate hash
    body_hash = calculate_body_hash(body)
    
    # Prepare skill data
    skill_data = {
        'name': normalized['name'],
        'body': body,
        'body_hash': body_hash,
        'metadata': normalized
    }
    
    # Database operation
    print("💾 Saving to database...")
    try:
        conn = get_db_connection()
        result = upsert_skill(conn, skill_data)
        conn.commit()
        conn.close()
    except Exception as e:
        return {'ok': False, 'error': f'Database error: {e}'}
    
    # Build response
    return {
        'ok': True,
        'skill_id': result['skill_id'],
        'name': skill_data['name'],
        'version': result['version'],
        'action': result['action'],
        'body_hash': body_hash[:16] + '...',
        'message': result['message']
    }


# ============================================================================
# CLI
# ============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Import a skill from Anthropic skills repository',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 import_skill.py https://github.com/anthropics/skills/blob/main/skills/webapp-testing/SKILL.md
  python3 import_skill.py https://raw.githubusercontent.com/anthropics/skills/main/skills/webapp-testing/SKILL.md

Environment Variables:
  SKILLS_DB_DSN: PostgreSQL connection string (required)
        """
    )
    
    parser.add_argument('url', help='GitHub URL to SKILL.md')
    parser.add_argument('--force', '-f', action='store_true', 
                       help='Force re-import even if unchanged')
    parser.add_argument('--json', action='store_true', 
                       help='Output results as JSON')
    
    args = parser.parse_args()
    
    # Import skill
    result = import_skill(args.url, force=args.force)
    
    # Output
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result.get('ok'):
            print(f"\n✅ {result['message']}")
            print(f"   Name: {result['name']}")
            print(f"   ID: {result['skill_id']}")
            print(f"   Version: {result['version']}")
            print(f"   Hash: {result['body_hash']}")
        else:
            print(f"\n❌ Error: {result['error']}")
            sys.exit(1)


if __name__ == '__main__':
    main()
