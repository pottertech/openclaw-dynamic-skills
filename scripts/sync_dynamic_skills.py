#!/usr/bin/env python3
"""Sync dynamic skills from DB to local folders."""

from __future__ import annotations

import argparse
import json
import os
import shutil
from pathlib import Path
from typing import Any

try:
    import psycopg2
    import psycopg2.extras
    PSYCOPG2_AVAILABLE = True
except ImportError:
    PSYCOPG2_AVAILABLE = False

import sys
sys.path.insert(0, str(Path(__file__).parent))
from render_skill_folder import render_skill


DEFAULT_LIMIT = 24


SQL_TOP_SKILLS = """
SELECT
  id,
  slug,
  name,
  title,
  description,
  category,
  tags,
  yaml_frontmatter,
  body_markdown,
  updated_at
FROM skills
WHERE enabled = true
ORDER BY priority ASC, updated_at DESC
LIMIT %s
"""


def fetch_skills(dsn: str, limit: int) -> list[dict[str, Any]]:
    """Fetch top skills from DB."""
    if not PSYCOPG2_AVAILABLE:
        raise ImportError("psycopg2 not installed")
    
    with psycopg2.connect(dsn) as conn:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(SQL_TOP_SKILLS, (limit,))
            return list(cur.fetchall())


def read_existing_dynamic_skill_dirs(out_root: Path) -> dict[str, Path]:
    """Find existing dynamic skill folders."""
    results: dict[str, Path] = {}
    if not out_root.exists():
        return results
    for child in out_root.iterdir():
        if child.is_dir() and (child / ".dynamic-skill.json").exists():
            results[child.name] = child
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--template-dir", required=True)
    parser.add_argument("--out-root", required=True)
    parser.add_argument("--limit", type=int, default=DEFAULT_LIMIT)
    parser.add_argument("--prune", action="store_true")
    args = parser.parse_args()
    
    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    
    try:
        selected = fetch_skills(args.dsn, args.limit)
    except ImportError as e:
        print(json.dumps({"error": str(e), "hint": "pip3 install psycopg2-binary"}))
        return 1
    
    selected_slugs: set[str] = set()
    
    for record in selected:
        path = render_skill(record, Path(args.template_dir), out_root)
        selected_slugs.add(path.name)
    
    if args.prune:
        existing = read_existing_dynamic_skill_dirs(out_root)
        for slug, path in existing.items():
            if slug not in selected_slugs:
                shutil.rmtree(path)
                print(f"Pruned: {slug}")
    
    print(json.dumps({
        "written": sorted(selected_slugs),
        "count": len(selected_slugs),
        "out_root": str(out_root),
        "pruned": bool(args.prune),
    }, indent=2))
    
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
