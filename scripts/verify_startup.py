#!/usr/bin/env python3
"""Verify dynamic-skills service can start."""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_dependencies():
    """Check all required dependencies."""
    print("Checking dependencies...")
    
    deps_ok = True
    
    # Check FastAPI
    try:
        import fastapi
        print("  ✓ FastAPI")
    except ImportError:
        print("  ✗ FastAPI (pip install fastapi)")
        deps_ok = False
    
    # Check psycopg2
    try:
        import psycopg2
        print("  ✓ psycopg2")
    except ImportError:
        print("  ✗ psycopg2 (pip install psycopg2-binary)")
        deps_ok = False
    
    # Check pydantic
    try:
        import pydantic
        print("  ✓ pydantic")
    except ImportError:
        print("  ✗ pydantic (pip install pydantic)")
        deps_ok = False
    
    # Check Redis (optional)
    try:
        import redis
        print("  ✓ Redis (optional)")
    except ImportError:
        print("  - Redis (optional, not installed)")
    
    # Check pgvector support
    print("\nChecking pgvector...")
    try:
        import psycopg2
        conn = psycopg2.connect(
            host=os.getenv("SKILLS_DB_HOST", "localhost"),
            port=os.getenv("SKILLS_DB_PORT", "5432"),
            database=os.getenv("SKILLS_DB_NAME", "openclaw_memory"),
            user=os.getenv("SKILLS_DB_USER", "openclaw"),
        )
        cur = conn.cursor()
        cur.execute("SELECT 1 FROM pg_extension WHERE extname = 'vector'")
        if cur.fetchone():
            print("  ✓ pgvector extension available")
        else:
            print("  ⚠ pgvector extension not installed (optional)")
        cur.close()
        conn.close()
    except Exception as e:
        print(f"  ⚠ Could not check pgvector: {e}")
    
    return deps_ok


def check_service_imports():
    """Check service module imports."""
    print("\nChecking service imports...")
    
    try:
        from services.lookup_service_v2 import app
        print("  ✓ lookup_service_v2 imports successfully")
        return True
    except Exception as e:
        print(f"  ✗ Failed to import lookup_service_v2: {e}")
        return False


def main():
    """Run all checks."""
    print("=" * 60)
    print("Dynamic Skills Startup Verification")
    print("=" * 60)
    print()
    
    deps_ok = check_dependencies()
    import_ok = check_service_imports()
    
    print()
    print("=" * 60)
    
    if deps_ok and import_ok:
        print("✓ All checks passed!")
        print()
        print("To start the service:")
        print("  python3 services/lookup_service_v2.py")
        return 0
    else:
        print("✗ Some checks failed")
        print()
        if not deps_ok:
            print("Install missing dependencies:")
            print("  pip install fastapi uvicorn psycopg2-binary pydantic")
        return 1


if __name__ == "__main__":
    sys.exit(main())