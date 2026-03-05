# 🚀 Dynamic Skills System - Complete Installation Guide

**For OpenClaw Beginners**  
**Version:** 1.0.0  
**Last Updated:** 2026-03-05

---

## 📋 What You're Installing

The **Dynamic Skills System** adds **60 pre-configured skills** to your OpenClaw installation, enabling automatic skill loading based on natural language queries.

**Includes:**
- ✅ 17 Anthropic original skills
- ✅ 25 Open Skills (community contributions)
- ✅ 3 Custom engineering skills (architect, tester, developer)
- ✅ 4 Custom media skills (ACE-Step, Kokoro, ComfyUI, business operations)
- ✅ 11 Utility skills (video, social, docker, analytics, backup, monitoring, project, calendar, cost, SEO, excalidraw)
- ✅ Semantic search with pgvector
- ✅ Redis caching (65x faster lookups)
- ✅ Auto-router integration
- ✅ Usage analytics

**Total:** 60 skills across 25+ categories

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites

You need:
- ✅ OpenClaw installed and running
- ✅ PostgreSQL 18 installed
- ✅ pgvector extension installed
- ✅ Python 3.9+ installed
- ✅ Redis (optional, for caching)


### One-Command Installation

```bash
# Navigate to release directory
cd ~/.openclaw/workspace/releases/dynamic-skills-v1.0.0

# Run installer
bash install.sh
```

That's it! The installer will:
1. Check prerequisites
2. Create database
3. Import all 60 skills
4. Generate embeddings
5. Start lookup service
6. Verify installation

---

## 📖 Detailed Installation

### Step 1: Check Prerequisites

```bash
# Check PostgreSQL
psql --version
# Should show: psql (PostgreSQL) 16.x or higher

# Check Python
python3 --version
# Should show: Python 3.9 or higher

# Check Redis (optional)
redis-cli ping
# Should show: PONG
```

**If missing:**

**macOS:**
```bash
# Install PostgreSQL 18 (recommended)
brew install postgresql@18

# Or PostgreSQL 16 (minimum supported)
brew install postgresql@18

# Install Redis
brew install redis

# Install pgvector
brew install pgvector
```

**Linux:**
```bash
sudo apt-get install postgresql postgresql-contrib
sudo apt-get install redis-server
sudo apt-get install postgresql-18-pgvector  # Adjust version number
```

### Step 2: Install pgvector Extension

```bash
# Connect to PostgreSQL
psql -U postgres

# Enable pgvector (required for semantic search)
CREATE EXTENSION IF NOT EXISTS vector;

# Verify
\dx | grep vector
# Should show: vector | 0.6.0 or higher

# Exit
\q
```


### Step 3: Run Installation

```bash
cd ~/.openclaw/workspace/releases/dynamic-skills-v1.0.0
bash install.sh
```

**What happens:**
1. ✅ Creates `skillsdb` database
2. ✅ Enables pgvector extension
3. ✅ Imports schema
4. ✅ Imports all 60 skills
5. ✅ Generates embeddings
6. ✅ Starts lookup service on port 8845
7. ✅ Verifies installation

### Step 4: Verify Installation

```bash
# Check health
curl http://localhost:8845/health

# Expected output:
# {"status":"healthy","skills_count":49}

# Test semantic search
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "test website", "max_skills": 3}'

# Expected: testing-webapps skill returned
```

### Step 5: Integrate with OpenClaw

**Add to OpenClaw configuration:**

```bash
# Set environment variable
export SKILLS_DB_DSN="postgresql://localhost:5432/skillsdb"

# Add to ~/.zshrc or ~/.bashrc for persistence
echo 'export SKILLS_DB_DSN="postgresql://localhost:5432/skillsdb"' >> ~/.zshrc
source ~/.zshrc
```

**Restart OpenClaw:**
```bash
openclaw gateway restart
```

---

## 🧪 Testing

### Test Semantic Search

```bash
# Test 1: Testing skills
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "test my login page with Playwright"}'

# Expected: testing-webapps skill

# Test 2: Development skills
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "write unit tests for my API"}'

# Expected: software-tester skill

# Test 3: Architecture skills
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "design a microservices system"}'

# Expected: systems-architect skill
```

### Test Auto-Router

**In OpenClaw, try:**

```
"I need to test my website with Playwright"
→ Should auto-load testing-webapps skill

"Write unit tests for my Python code"
→ Should auto-load software-tester skill

"Design a scalable database architecture"
→ Should auto-load systems-architect skill
```

---

## 📁 What's Installed

### Database (skillsdb)

**Tables:**
- `skills` - Skill definitions (49 rows)
- `skill_chunks` - Progressive disclosure chunks (100+ rows)
- `skill_usage_logs` - Usage analytics
- `skill_embeddings` - Vector embeddings for semantic search

### Services

**Lookup Service:**
- Port: 8845
- Endpoint: `http://localhost:8845`
- Health: `http://localhost:8845/health`
- Lookup: `POST /skills/lookup`

### Files

```
~/.openclaw/workspace/releases/dynamic-skills-v1.0.0/
├── README.md                  # This guide
├── install.sh                 # Installation script
├── package.json               # Version metadata
├── requirements.txt           # Python dependencies
├── sql/
│   ├── import.sql            # Complete database import
│   ├── schema.sql            # Database schema
│   ├── skills_data.sql       # All 60 skills
│   └── skill_chunks_data.sql # Chunk data
├── scripts/
│   ├── import_skill.py       # Import single skill
│   ├── generate_embeddings.py # Generate embeddings
│   └── skills_scanner.py     # Discover new skills
├── services/
│   └── lookup_service_v2.py   # Lookup service
├── tools/
│   └── skills_lookup.py       # Python client
└── skills/                    # Skill source files
    ├── systems-architect/
    ├── software-tester/
    ├── software-developer/
    └── ... (46 more)
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
export SKILLS_DB_DSN="postgresql://localhost:5432/skillsdb"

# Optional (Redis caching)
export REDIS_URL="redis://localhost:6379"
export REDIS_TTL=3600

# Optional (Lookup service)
export LOOKUP_SERVICE_PORT=8845
export LOOKUP_SERVICE_HOST=127.0.0.1
```

### OpenClaw Integration

**Add to OpenClaw config (`~/.openclaw/config.json`):**

```json
{
  "skills": {
    "dynamic": {
      "enabled": true,
      "database": "postgresql://localhost:5432/skillsdb",
      "lookup_service": "http://localhost:8845",
      "auto_load": true,
      "cache_ttl": 3600
    }
  }
}
```

---

## 🐛 Troubleshooting

### Issue: "Database not found"

**Solution:**
```bash
# Create database manually
createdb skillsdb

# Enable pgvector
psql -d skillsdb -c "CREATE EXTENSION IF NOT EXISTS vector;"

# Re-run import
psql -d skillsdb -f sql/import.sql
```

### Issue: "pgvector extension not found"

**Solution:**
```bash
# Install pgvector
# macOS
brew install pgvector

# Linux
sudo apt-get install postgresql-16-pgvector

# Enable extension
psql -U postgres -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

### Issue: "Lookup service not starting"

**Solution:**
```bash
# Check if port is in use
lsof -i :8845

# Kill existing process
kill $(lsof -t -i :8845)

# Check dependencies
pip3 install -r requirements.txt

# Start manually
cd services
python3 lookup_service_v2.py
```

### Issue: "Skills not found in search"

**Solution:**
```bash
# Regenerate embeddings
cd scripts
python3 generate_embeddings.py

# Verify skills count
psql -d skillsdb -c "SELECT COUNT(*) FROM skills WHERE status='active';"
# Should return: 49
```

### Issue: "Router not auto-loading skills"

**Solution:**
```bash
# Check OpenClaw logs
openclaw logs | grep skill

# Verify environment variable
echo $SKILLS_DB_DSN
# Should show: postgresql://localhost:5432/skillsdb

# Restart OpenClaw
openclaw gateway restart
```

---

## 📊 Performance

### Benchmarks

| Operation | Without Cache | With Redis |
|-----------|--------------|------------|
| Semantic Search | ~100ms | ~6ms |
| Keyword Search | ~50ms | ~5ms |
| Router Overhead | <50ms | <50ms |
| **Total** | **<150ms** | **<60ms** |

### Optimization Tips

1. **Enable Redis caching** - 65x faster lookups
2. **Use appropriate max_skills** - Don't request more than needed
3. **Monitor usage** - Check skill_usage_logs table
4. **Regular maintenance** - Vacuum database weekly

---

## 📈 Usage Analytics

### Check Skill Usage

```bash
psql -d skillsdb -c "
SELECT s.name, COUNT(*) as usage_count
FROM skill_usage_logs sul
JOIN skills s ON sul.skill_id = s.id
GROUP BY s.name
ORDER BY usage_count DESC
LIMIT 10;
"
```

### Monitor Performance

```bash
psql -d skillsdb -c "
SELECT 
  DATE(created_at) as date,
  COUNT(*) as queries,
  AVG(response_time_ms) as avg_time_ms
FROM skill_usage_logs
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 7;
"
```

---

## 🎓 Next Steps

### Learn More

- **Skill Catalog:** See `docs/SKILLS-CATALOG.md` for all 60 skills
- **API Reference:** See `docs/API-REFERENCE.md` for lookup service
- **Best Practices:** See `docs/BEST-PRACTICES.md` for usage tips

### Customize

- **Add New Skills:** Use `scripts/import_skill.py`
- **Modify Existing:** Edit skills in `skills/` directory
- **Create Custom Skills:** Follow `docs/CREATE-SKILL.md`

### Maintain

- **Weekly:** Run `scripts/skills_scanner.py --scan` for new skills
- **Monthly:** Review usage analytics, remove unused skills
- **Quarterly:** Update skills from upstream sources

---

## 🆘 Getting Help

### Documentation

- `README.md` - This guide
- `docs/` - Detailed documentation
- `examples/` - Usage examples

### Logs

- Lookup service: Console output
- Database: `~/Library/Logs/postgresql.log` (macOS) or `/var/log/postgresql/` (Linux)
- OpenClaw: `openclaw logs`

### Community

- **Discord:** https://discord.com/invite/clawd
- **GitHub:** https://github.com/openclaw/openclaw
- **ClawHub:** https://clawhub.com

---

## ✅ Success Checklist

After installation, verify:

- [ ] Database created (`skillsdb`)
- [ ] 60 skills imported
- [ ] Embeddings generated
- [ ] Lookup service running (port 8845)
- [ ] Health check passes
- [ ] Semantic search works
- [ ] OpenClaw integration working
- [ ] Auto-router loading skills

---

**Congratulations! You're ready to use the Dynamic Skills System!** 🎉

---

*Last Updated: 2026-03-05*  
*Version: 1.0.0*  
*Total Skills: 49*
