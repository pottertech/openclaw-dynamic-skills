# 🧭 Dynamic Skill Loader

**Automatically load relevant skills when tasks require specialized workflows.**

---

## Purpose

This router skill monitors task descriptions and automatically triggers `skills.lookup` when specialized procedures are needed.

---

## Trigger Conditions

### ALWAYS Call `skills.lookup` When:

#### 1. Installation/Setup Tasks
- Keywords: `install`, `setup`, `configure`, `initialize`, `deploy`
- Examples:
  - "Install Playwright for testing"
  - "Setup n8n workflow automation"
  - "Configure FFmpeg for video processing"

#### 2. Debugging Tasks
- Keywords: `debug`, `troubleshoot`, `fix`, `error`, `issue`, `problem`
- Examples:
  - "Debug UI automation failing"
  - "Troubleshoot video encoding errors"
  - "Fix MQTT connection issues"

#### 3. Specialized Tool Usage
- Tools: `playwright`, `ffmpeg`, `mqtt`, `n8n`, `wordpress`, `comfyui`, `huggingface`
- Examples:
  - "Use Playwright to test login flow"
  - "Process video with FFmpeg"
  - "Create n8n automation workflow"

#### 4. Multi-Step Workflows
- Indicators: 3+ sequential steps, complex procedures
- Examples:
  - "First install dependencies, then build, then deploy"
  - "Download video, extract audio, transcribe, summarize"

### NEVER Call `skills.lookup` When:

- Simple file operations (read, write, delete, move)
- Basic shell commands (ls, cd, pwd, cat)
- Conversational tasks (questions, explanations)
- Already called for this specific task session
- Task is purely creative (writing, design without technical steps)

---

## Process

### Step 1: Analyze Task

Extract keywords and intent:
```python
task = "Install Playwright and test the login flow"

# Extract keywords
keywords = ['install', 'playwright', 'test', 'login']

# Determine category
if 'install' in keywords or 'setup' in keywords:
    category = 'installation'
elif 'playwright' in keywords or 'test' in keywords:
    category = 'testing'
```

### Step 2: Create Query

Build search query from keywords:
```python
query = ' '.join(keywords)  # "install playwright test login"
```

### Step 3: Call skills.lookup

```python
result = skills.lookup(
    query=query,
    task_summary=task,
    max_skills=2,
    search_type='hybrid'
)
```

### Step 4: Integrate Instructions

Use returned skill excerpts to guide execution:
```markdown
Based on the `webapp-testing` skill:

1. Install Playwright: `pip install playwright`
2. Install browsers: `playwright install`
3. Write test script using `sync_playwright`
4. Run test and capture results
```

---

## Implementation

### OpenClaw Skill File

```markdown
---
name: dynamic-skill-loader
description: Automatically load specialized workflow instructions when tasks require multi-step procedures or specialized tools.
user-invocable: false
metadata:
  openclaw:
    emoji: library
    requires:
      bins: [python3]
      tools: [skills.lookup]
---

## Dynamic Skill Loader

I automatically detect when you need specialized procedures and load the appropriate skill instructions.

### When I Activate:

- Installation/setup tasks
- Debugging complex issues  
- Using specialized tools (Playwright, FFmpeg, MQTT, n8n, etc.)
- Multi-step workflows (3+ steps)

### How I Work:

1. **Analyze** your task for trigger keywords
2. **Query** the skills database
3. **Integrate** relevant instructions
4. **Execute** with proper procedures

### Example:

**You:** "I need to test the login flow with Playwright"

**Me:** [Detects: testing + playwright]
      [Calls: skills.lookup(query="playwright test login")]
      [Returns: webapp-testing skill]
      [Executes with proper Playwright procedures]

---

**I make sure you're following best practices without you having to ask!**
```

---

## Usage Examples

### Example 1: Installation Task

**User:** "Install and configure FFmpeg for video processing"

**Router Detection:**
- Keywords: `install`, `configure`, `ffmpeg`
- Category: Installation + Specialized Tool
- Action: Call `skills.lookup("ffmpeg install configure")`

**Result:** Returns FFmpeg skill with installation steps

---

### Example 2: Debugging Task

**User:** "My Playwright test is failing on login, help me debug"

**Router Detection:**
- Keywords: `playwright`, `test`, `failing`, `debug`, `login`
- Category: Debugging + Testing
- Action: Call `skills.lookup("debug playwright test login")`

**Result:** Returns webapp-testing skill with debugging procedures

---

### Example 3: Multi-Step Workflow

**User:** "I want to download a YouTube video, extract audio, and transcribe it"

**Router Detection:**
- Keywords: `download`, `youtube`, `extract`, `audio`, `transcribe`
- Category: Multi-step workflow (3 steps)
- Action: Call `skills.lookup("youtube download audio transcription")`

**Result:** Returns relevant skills for each step

---

## Rate Limiting

To prevent excessive lookups:

- **Max 1 lookup per task** (unless task fundamentally changes)
- **Cache results** for same query within 5 minutes
- **Skip lookup** if task is simple (<3 steps, no specialized tools)

---

## Error Handling

### If skills.lookup Fails:

1. **Service unavailable:** Fall back to built-in knowledge
2. **No relevant skills:** Proceed with general approach
3. **Timeout:** Continue without skill instructions

### Logging:

Always log lookup attempts:
```python
log_usage(
    query=query,
    success=True/False,
    skills_returned=len(results),
    task_summary=task
)
```

---

## Testing

### Test Cases:

1. **Should Trigger:**
   - "Install Playwright" ✓
   - "Debug FFmpeg encoding error" ✓
   - "Setup n8n workflow" ✓
   - "Test website with automated scripts" ✓

2. **Should NOT Trigger:**
   - "What's 2+2?" ✓
   - "Write a poem about coding" ✓
   - "List files in directory" ✓
   - "Read this file" ✓

---

## Performance

- **Lookup latency:** <100ms (with Redis cache)
- **Decision time:** <50ms
- **Overhead:** Negligible (<150ms total)

---

*Part of OpenClaw Dynamic Skills System v3.0*
