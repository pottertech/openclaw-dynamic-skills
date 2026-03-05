# 🎯 Quick Start - Dynamic Skills System

**Get started in 2 minutes!**

---

## ⚡ One-Command Install

```bash
cd ~/.openclaw/workspace/releases/dynamic-skills-v1.0.0
bash install.sh
```

That's it! ✅

---

## 🧪 Test It

```bash
# Check health
curl http://localhost:8845/health

# Test search
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "test website"}'
```

---

## 📖 What You Get

**49 Pre-configured Skills:**
- 17 Anthropic originals
- 25 community skills
- 3 engineering skills (architect, tester, developer)
- 4 media skills (music, images, video, business)

**Features:**
- ✅ Semantic search (find skills by natural language)
- ✅ Auto-loading (router detects when to use skills)
- ✅ Redis caching (65x faster)
- ✅ Usage analytics

---

## 🚀 Use with OpenClaw

**In OpenClaw, just ask:**

```
"I need to test my login page"
→ Auto-loads testing-webapps skill

"Write unit tests for my API"
→ Auto-loads software-tester skill

"Design a microservices system"
→ Auto-loads systems-architect skill
```

No manual skill lookup needed!

---

## 📚 Documentation

- **INSTALL.md** - Complete installation guide
- **docs/SKILLS-CATALOG.md** - All 49 skills listed
- **README.md** - Full documentation

---

## 🆘 Troubleshooting

**Service not starting?**
```bash
# Check logs
cat /tmp/lookup_service.log

# Restart manually
cd services
python3 lookup_service_v2.py
```

**Skills not found?**
```bash
# Regenerate embeddings
python3 scripts/generate_embeddings.py
```

**Database error?**
```bash
# Recreate database
dropdb skillsdb
createdb skillsdb
psql -d skillsdb -c "CREATE EXTENSION vector;"
psql -d skillsdb -f sql/import.sql
```

---

**Need help?** Check `INSTALL.md` or join Discord: https://discord.com/invite/clawd
