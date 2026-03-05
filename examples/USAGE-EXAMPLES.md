# 🔧 Example Usage - Dynamic Skills System

**Real-world examples of using the skills lookup system**

---

## 1. Semantic Search Examples

### Basic Search

```bash
# Find testing skills
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "test my website with Playwright"}'

# Response:
{
  "skills": [
    {
      "name": "testing-webapps",
      "similarity_score": 0.508,
      "description": "Test web applications with Playwright"
    }
  ]
}
```

### Multiple Results

```bash
# Find development skills
curl -X POST http://localhost:8845/skills/lookup \
  -H "Content-Type: application/json" \
  -d '{"query": "write code for my app", "max_skills": 5}'

# Returns: software-developer, building-claude-apps, creating-skills, etc.
```

---

## 2. Python Client Usage

```python
from skills_lookup import SkillsLookup

# Initialize
lookup = SkillsLookup()

# Search
results = lookup.search("test my login page", max_skills=3)

for skill in results:
    print(f"Skill: {skill['name']}")
    print(f"Score: {skill['similarity_score']}")
    print(f"Description: {skill['description']}")
    print()
```

---

## 3. OpenClaw Integration

### Automatic Skill Loading

**User asks:**
```
"I need to test my website's checkout flow"
```

**Router automatically:**
1. Queries lookup service
2. Gets `testing-webapps` skill
3. Loads skill context
4. Provides expert guidance

**No manual intervention needed!**

---

## 4. Real Workflows

### Workflow 1: Testing a New Feature

**User:** "I just built a login page, how do I test it?"

**System loads:** `testing-webapps` skill

**Guidance provided:**
```markdown
## Testing Your Login Page with Playwright

### 1. Install Playwright
```bash
npm install -D @playwright/test
npx playwright install
```

### 2. Create Test File
```javascript
// tests/login.spec.js
import { test, expect } from '@playwright/test';

test('login works', async ({ page }) => {
  await page.goto('/login');
  await page.fill('input[name="email"]', 'user@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page).toHaveURL('/dashboard');
});
```

### 3. Run Test
```bash
npx playwright test
```
```

---

### Workflow 2: Designing a System

**User:** "I need to design a scalable API for my startup"

**System loads:** `systems-architect` skill

**Guidance provided:**
```markdown
## Scalable API Architecture

### Recommended Stack:
- **API Gateway:** Kong or AWS API Gateway
- **Services:** Microservices architecture
- **Database:** PostgreSQL with read replicas
- **Cache:** Redis for hot data
- **Queue:** Kafka for async processing

### Key Considerations:
1. **Authentication:** JWT tokens
2. **Rate Limiting:** 1000 req/min per user
3. **Monitoring:** Prometheus + Grafana
4. **Scaling:** Horizontal auto-scaling

### Initial Architecture:
[Client] → [API Gateway] → [Services] → [Database]
                              ↓
                         [Redis Cache]
```

---

### Workflow 3: Writing Tests

**User:** "How do I write unit tests for my Python code?"

**System loads:** `software-tester` skill

**Guidance provided:**
```markdown
## Unit Testing with pytest

### 1. Install pytest
```bash
pip install pytest pytest-cov
```

### 2. Write Tests
```python
# test_calculator.py
def test_add():
    assert add(2, 3) == 5

def test_divide_by_zero():
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)
```

### 3. Run Tests
```bash
pytest                    # All tests
pytest -v                 # Verbose
pytest --cov=app          # With coverage
```

### 4. Best Practices:
- Test one thing per test
- Use descriptive names
- Mock external dependencies
- Aim for 80%+ coverage
```

---

### Workflow 4: Creating Music

**User:** "I want to create background music for my video"

**System loads:** `ace-step-music` skill

**Guidance provided:**
```markdown
## Creating Background Music with ACE-Step

### 1. Start ACE-Step
```bash
cd ~/ACE-Step
python3 gradio_ui.py
```

### 2. Generate Music
- Open http://localhost:7860
- Prompt: "Upbeat corporate background music"
- Duration: 30 seconds
- Style: Corporate, motivational

### 3. Download & Use
- Download generated WAV
- Import to video editor
- Adjust volume to -20dB
```

---

## 5. Advanced Usage

### Batch Processing

```python
from skills_lookup import SkillsLookup

lookup = SkillsLookup()

queries = [
    "test website",
    "write unit tests",
    "design database",
    "create music",
    "encrypt files"
]

for query in queries:
    results = lookup.search(query, max_skills=1)
    print(f"{query:20} → {results[0]['name']}")
```

**Output:**
```
test website         → testing-webapps
write unit tests     → software-tester
design database      → systems-architect
create music         → ace-step-music
encrypt files        → age-file-encryption
```

---

### Usage Analytics

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

**Example Output:**
```
name                    | usage_count
------------------------+-------------
testing-webapps         | 145
software-developer      | 98
systems-architect       | 87
software-tester         | 76
ace-step-music          | 54
```

---

## 6. Custom Integrations

### Slack Bot

```python
from flask import Flask, request, jsonify
from skills_lookup import SkillsLookup

app = Flask(__name__)
lookup = SkillsLookup()

@app.route('/slack/skill', methods=['POST'])
def slack_skill():
    data = request.json
    query = data['text']
    
    results = lookup.search(query, max_skills=3)
    
    response = {
        "text": f"Found {len(results)} relevant skills:",
        "attachments": [
            {
                "title": skill['name'],
                "text": skill['description'],
                "color": "good"
            }
            for skill in results
        ]
    }
    
    return jsonify(response)
```

---

### CLI Tool

```python
#!/usr/bin/env python3
# skills-cli

import sys
from skills_lookup import SkillsLookup

def main():
    if len(sys.argv) < 2:
        print("Usage: skills-cli <query>")
        sys.exit(1)
    
    query = ' '.join(sys.argv[1:])
    lookup = SkillsLookup()
    results = lookup.search(query, max_skills=5)
    
    print(f"Found {len(results)} skills for '{query}':\n")
    for i, skill in enumerate(results, 1):
        print(f"{i}. {skill['name']}")
        print(f"   {skill['description']}")
        print(f"   Score: {skill['similarity_score']:.3f}")
        print()

if __name__ == '__main__':
    main()
```

**Usage:**
```bash
./skills-cli test website
./skills-cli write unit tests
./skills-cli design microservices
```

---

## 7. Performance Tips

### Enable Caching

```bash
# Start Redis
redis-server

# Lookup service will auto-detect and use cache
# Results: 65x faster!
```

### Batch Queries

```python
# ❌ Slow (one at a time)
for query in queries:
    lookup.search(query)

# ✅ Fast (parallel)
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(lookup.search, queries))
```

---

## 8. Monitoring

### Health Check Endpoint

```bash
curl http://localhost:8845/health

# Response:
{
  "status": "healthy",
  "skills_count": 49,
  "cache_enabled": true,
  "uptime_seconds": 3600
}
```

### Query Logging

```bash
# View recent queries
tail -f /tmp/lookup_service.log | grep "Query:"
```

---

**More examples in:** `examples/` directory
