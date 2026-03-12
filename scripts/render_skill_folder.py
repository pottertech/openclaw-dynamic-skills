#!/usr/bin/env python3
"""Render DB skill record to local skill folder."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
from pathlib import Path

try:
    from jinja2 import Environment, FileSystemLoader
    JINJA_AVAILABLE = True
except ImportError:
    JINJA_AVAILABLE = False


def slugify(value: str) -> str:
    """Convert to URL-friendly slug."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value or "skill"


def render_skill_jinja(record: dict, template_dir: Path, skill_dir: Path) -> None:
    """Render skill using Jinja2 template."""
    env = Environment(loader=FileSystemLoader(str(template_dir)))
    template = env.get_template("SKILL.md.j2")
    
    frontmatter = record.get("yaml_frontmatter") or {}
    body = template.render(
        slug=record.get("slug"),
        name=record.get("name"),
        title=record.get("title"),
        description=record.get("description"),
        frontmatter=frontmatter,
        body_markdown=record.get("body_markdown", "").strip(),
    )
    
    (skill_dir / "SKILL.md").write_text(body, encoding="utf-8")


def render_skill_basic(record: dict, skill_dir: Path) -> None:
    """Render skill without Jinja2 (fallback)."""
    slug = record.get("slug", "skill")
    name = record.get("name", slug)
    title = record.get("title", name)
    description = record.get("description", "")
    body = record.get("body_markdown", "").strip()
    
    frontmatter = record.get("yaml_frontmatter") or {}
    
    # Build frontmatter YAML
    fm_lines = ["---"]
    fm_lines.append(f'name: {frontmatter.get("name", name)}')
    fm_lines.append(f'description: "{description}"')
    
    if frontmatter.get("tools"):
        fm_lines.append("tools:")
        for tool in frontmatter["tools"]:
            fm_lines.append(f"  - {tool}")
    
    if frontmatter.get("metadata"):
        fm_lines.append("metadata:")
        for key, value in frontmatter["metadata"].items():
            fm_lines.append(f"  {key}: {json.dumps(value)}")
    
    fm_lines.append("---")
    fm_lines.append("")
    fm_lines.append(f"# {title}")
    fm_lines.append("")
    fm_lines.append(body)
    fm_lines.append("")
    
    (skill_dir / "SKILL.md").write_text("\n".join(fm_lines), encoding="utf-8")


def render_skill(record: dict, template_dir: Path, out_root: Path) -> Path:
    """Render one skill to folder."""
    slug = slugify(record.get("slug") or record.get("name") or "skill")
    skill_dir = out_root / slug
    skill_dir.mkdir(parents=True, exist_ok=True)
    
    if JINJA_AVAILABLE and (template_dir / "SKILL.md.j2").exists():
        render_skill_jinja(record, template_dir, skill_dir)
    else:
        render_skill_basic(record, skill_dir)
    
    # Write manifest
    manifest = {
        "id": record.get("id"),
        "slug": slug,
        "category": record.get("category"),
        "tags": record.get("tags", []),
        "updated_at": record.get("updated_at"),
    }
    (skill_dir / ".dynamic-skill.json").write_text(
        json.dumps(manifest, indent=2),
        encoding="utf-8",
    )
    
    return skill_dir


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record-json", required=True)
    parser.add_argument("--template-dir", required=True)
    parser.add_argument("--out-root", required=True)
    args = parser.parse_args()
    
    record = json.loads(args.record_json)
    render_skill(record, Path(args.template_dir), Path(args.out_root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
