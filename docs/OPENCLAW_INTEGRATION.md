# OpenClaw Integration Guide

## Overview

OpenClaw loads skills from local skill folders, not directly from a database. This project makes dynamic skills work by selecting skills from PostgreSQL and writing them to OpenClaw-compatible local directories as standard SKILL.md files.

## How It Works

```
PostgreSQL (source of truth)
    ↓
Lookup Service (ranking and retrieval)
    ↓
Renderer/Sync (writes real local skill folders)
    ↓
OpenClaw (reads those local SKILL.md files normally)
```

## Components

### 1. Sync Scripts (`scripts/`)
- `render_skill_folder.py` - Renders one DB record to local folder
- `sync_dynamic_skills.py` - Syncs top N skills to workspace

### 2. Plugin (`plugin/`)
- TypeScript plugin with agent tools
- `dynamic_skill_search` - Search skills
- `dynamic_skill_activate` - Write skills to disk

### 3. Hooks (`hooks/`)
- `dynamic-skills-prefetch` - Auto-fetches on session start

### 4. Templates (`templates/`)
- `SKILL.md.j2` - Jinja2 template for rendering

## Installation

### 1. Prerequisites
- PostgreSQL with pgvector extension
- Python 3.10+
- Node.js 18+ (for plugin build)

### 2. Install
```bash
# Clone
git clone https://github.com/pottertech/openclaw-dynamic-skills.git
cd openclaw-dynamic-skills

# Install Python deps
pip3 install -r requirements.txt

# Install Jinja2 (optional but recommended)
pip3 install jinja2

# Build plugin (if using TypeScript plugin)
cd plugin
npm install
npm run build
```

### 3. Configure

Add to `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "dynamic-skills": {
        "enabled": true,
        "baseUrl": "http://127.0.0.1:8845",
        "workspaceMode": "workspace",
        "workspaceSubdir": "skills/dynamic",
        "maxActiveSkills": 8
      }
    }
  },
  "tools": {
    "allow": ["*", "dynamic_skill_search", "dynamic_skill_activate"]
  }
}
```

### 4. Start Services

```bash
# Start lookup service
python3 services/lookup_service_v2.py &

# Enable hook (if shipped separately)
openclaw hooks enable dynamic-skills-prefetch
```

## Usage

### Manual Sync

```bash
# Sync top 12 skills to managed directory
python3 scripts/sync_dynamic_skills.py \
  --dsn "postgresql://localhost:5432/skillsdb" \
  --template-dir templates \
  --out-root "$HOME/.openclaw/skills/dynamic" \
  --limit 12 \
  --prune
```

### Plugin Tools

Agent can call:
- `dynamic_skill_search` - Find matching skills
- `dynamic_skill_activate` - Write them to workspace

### Hook Flow

1. Session starts
2. Hook reads incoming message
3. Calls `/lookup` with message text
4. Writes top N skills to `<workspace>/skills/dynamic/`
5. Agent runs with those skills available

## Workspace Mode vs Managed Mode

### Workspace Mode (Recommended)
- Skills written to `<workspace>/skills/dynamic/`
- Task-specific, highest precedence
- Overrides global and bundled skills

### Managed Mode
- Skills written to `~/.openclaw/skills/dynamic/`
- Global shared skills
- Good for always-on capabilities

## Troubleshooting

### Skills not appearing
1. Check lookup service is running: `curl http://localhost:8845/health`
2. Verify sync wrote files: `ls ~/.openclaw/skills/dynamic/`
3. Check OpenClaw loaded them: `openclaw skills list`

### Plugin not loading
1. Check plugin manifest: `openclaw plugins list`
2. Verify plugin config in `~/.openclaw/openclaw.json`
3. Check for errors: `openclaw plugins doctor`

### Hook not firing
1. Check hook is enabled: `openclaw hooks list`
2. Verify event subscription in `hook.json`
3. Check logs for errors

## Architecture

See `ARCHITECTURE.md` for detailed system design.

## License

MIT - See LICENSE
