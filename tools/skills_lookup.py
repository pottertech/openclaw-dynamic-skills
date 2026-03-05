#!/usr/bin/env python3
"""
OpenClaw Dynamic Skills — Tool Wrapper

OpenClaw tool for skills.lookup

Installation:
    Link to ~/.openclaw/tools/skills_lookup.py
    
Usage (from OpenClaw):
    skills.lookup(query="test web app", task_summary="debug UI", max_skills=2)
"""

import os
import sys
import json
import requests
from typing import List, Dict, Any, Optional


# Configuration
LOOKUP_SERVICE_URL = os.getenv('SKILLS_LOOKUP_SERVICE_URL', 'http://localhost:8845')
API_KEY = os.getenv('SKILLS_LOOKUP_API_KEY', '')


def lookup_skills(
    query: str,
    task_summary: Optional[str] = None,
    max_skills: int = 2,
    agent_name: Optional[str] = None,
    search_type: str = 'hybrid'
) -> Dict[str, Any]:
    """
    Lookup relevant skills from the dynamic skills service.
    
    Args:
        query: Search query (keywords from task)
        task_summary: Optional task context
        max_skills: Maximum number of skills to return
        agent_name: Agent making request ('arty' or 'brodie')
    
    Returns:
        Dict with skills list and metadata
    """
    try:
        # Prepare request
        payload = {
            'query': query,
            'task_summary': task_summary,
            'max_skills': max_skills,
            'search_type': search_type
        }
        
        if agent_name:
            payload['agent_name'] = agent_name
        
        # Prepare headers
        headers = {
            'Content-Type': 'application/json'
        }
        
        if API_KEY:
            headers['X-API-Key'] = API_KEY
        
        # Make request
        response = requests.post(
            f"{LOOKUP_SERVICE_URL}/skills/lookup",
            json=payload,
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        result = response.json()
        
        return {
            'ok': True,
            'skills': result.get('skills', []),
            'count': result.get('count', 0),
            'query': result.get('query', query)
        }
        
    except requests.exceptions.ConnectionError:
        return {
            'ok': False,
            'error': 'Skills lookup service not available',
            'skills': []
        }
    except requests.exceptions.Timeout:
        return {
            'ok': False,
            'error': 'Skills lookup service timeout',
            'skills': []
        }
    except Exception as e:
        return {
            'ok': False,
            'error': str(e),
            'skills': []
        }


def get_skill(skill_id: str) -> Dict[str, Any]:
    """
    Get full skill by ID.
    
    Args:
        skill_id: Skill UUID/XID
    
    Returns:
        Dict with full skill data
    """
    try:
        headers = {'Content-Type': 'application/json'}
        if API_KEY:
            headers['X-API-Key'] = API_KEY
        
        response = requests.get(
            f"{LOOKUP_SERVICE_URL}/skills/{skill_id}",
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        return {
            'ok': True,
            'skill': response.json()
        }
        
    except Exception as e:
        return {
            'ok': False,
            'error': str(e)
        }


def list_skills(status: str = 'active', limit: int = 50) -> Dict[str, Any]:
    """
    List all skills.
    
    Args:
        status: Filter by status (active, deprecated, archived)
        limit: Maximum results
    
    Returns:
        Dict with skills list
    """
    try:
        headers = {'Content-Type': 'application/json'}
        if API_KEY:
            headers['X-API-Key'] = API_KEY
        
        response = requests.get(
            f"{LOOKUP_SERVICE_URL}/skills",
            params={'status': status, 'limit': limit},
            headers=headers,
            timeout=10
        )
        
        response.raise_for_status()
        return {
            'ok': True,
            'skills': response.json().get('skills', []),
            'count': response.json().get('count', 0)
        }
        
    except Exception as e:
        return {
            'ok': False,
            'error': str(e)
        }


# OpenClaw tool interface
def main():
    """CLI interface for testing."""
    if len(sys.argv) < 2:
        print("Usage: python3 skills_lookup.py <command> [args]")
        print("Commands:")
        print("  lookup <query> [max_skills]")
        print("  get <skill_id>")
        print("  list [status] [limit]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'lookup':
        query = sys.argv[2] if len(sys.argv) > 2 else ''
        max_skills = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        
        result = lookup_skills(query=query, max_skills=max_skills)
        print(json.dumps(result, indent=2))
        
    elif command == 'get':
        skill_id = sys.argv[2] if len(sys.argv) > 2 else ''
        result = get_skill(skill_id)
        print(json.dumps(result, indent=2))
        
    elif command == 'list':
        status = sys.argv[2] if len(sys.argv) > 2 else 'active'
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
        
        result = list_skills(status=status, limit=limit)
        print(json.dumps(result, indent=2))
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
