#!/usr/bin/env python3
"""
OpenClaw Dynamic Skills — Router Skill (Phase 3)

Automatically triggers skills.lookup when tasks require specialized procedures.

Usage:
    from router import should_lookup, create_query
    if should_lookup(task):
        query = create_query(task)
        results = skills_lookup(query)
"""

import re
from typing import List, Tuple, Optional


# ============================================================================
# TRIGGER PATTERNS
# ============================================================================

INSTALL_KEYWORDS = [
    'install', 'setup', 'configure', 'initialize', 'deploy',
    'setup', 'prepare', 'enable', 'activate'
]

DEBUG_KEYWORDS = [
    'debug', 'troubleshoot', 'fix', 'error', 'issue', 'problem',
    'broken', 'failing', 'not working', 'crash', 'bug'
]

SPECIALIZED_TOOLS = {
    'playwright': ['playwright', 'browser automation', 'e2e test', 'automated scripts'],
    'ffmpeg': ['ffmpeg', 'video processing', 'audio extraction', 'transcoding'],
    'mqtt': ['mqtt', 'message queue', 'iot messaging'],
    'n8n': ['n8n', 'workflow automation', 'zapier alternative'],
    'wordpress': ['wordpress', 'wp-cli', 'wp'],
    'comfyui': ['comfyui', 'stable diffusion', 'image generation'],
    'huggingface': ['huggingface', 'transformers', 'diffusers'],
    'docker': ['docker', 'container', 'dockerfile'],
    'kubernetes': ['kubernetes', 'k8s', 'kubectl'],
    'git': ['git', 'version control', 'commit', 'push', 'pull']
}

MULTI_STEP_INDICATORS = [
    'first.*then', 'step.*step', 'after.*before',
    'download.*extract.*transcribe',
    'install.*build.*deploy',
    'setup.*configure.*test'
]

SKIP_KEYWORDS = [
    'what is', 'explain', 'define', 'describe',
    'write a poem', 'write a story', 'creative',
    'list files', 'read file', 'show me',
    'simple', 'basic', 'quick'
]


# ============================================================================
# DETECTION FUNCTIONS
# ============================================================================

def contains_install(task: str) -> bool:
    """Check if task involves installation/setup."""
    task_lower = task.lower()
    return any(keyword in task_lower for keyword in INSTALL_KEYWORDS)


def contains_debug(task: str) -> bool:
    """Check if task involves debugging."""
    task_lower = task.lower()
    return any(keyword in task_lower for keyword in DEBUG_KEYWORDS)


def detect_specialized_tool(task: str) -> Optional[str]:
    """Detect if task mentions a specialized tool."""
    task_lower = task.lower()
    
    for tool, patterns in SPECIALIZED_TOOLS.items():
        if any(pattern in task_lower for pattern in patterns):
            return tool
    
    return None


def is_multi_step(task: str) -> bool:
    """Check if task requires multiple steps."""
    task_lower = task.lower()
    
    # Check for multi-step patterns
    for pattern in MULTI_STEP_INDICATORS:
        if re.search(pattern, task_lower):
            return True
    
    # Count sequential action verbs
    action_verbs = ['install', 'build', 'test', 'deploy', 'run', 'create', 'download', 'extract']
    count = sum(1 for verb in action_verbs if verb in task_lower)
    
    return count >= 3


def should_skip(task: str) -> bool:
    """Check if task should skip lookup."""
    task_lower = task.lower()
    
    # Simple file operations
    if any(op in task_lower for op in ['read file', 'write file', 'delete file', 'list files', 'ls ', 'cd ', 'pwd']):
        return True
    
    # Conversational/educational
    if any(skip in task_lower for skip in SKIP_KEYWORDS):
        return True
    
    # Very short tasks (<10 words, no technical keywords)
    if len(task.split()) < 10:
        technical_terms = ['api', 'database', 'server', 'code', 'script', 'tool']
        if not any(term in task_lower for term in technical_terms):
            return True
    
    return False


def should_lookup(task: str) -> bool:
    """
    Determine if task should trigger skills.lookup.
    
    Returns True if:
    - Installation/setup task
    - Debugging task
    - Uses specialized tool
    - Multi-step workflow
    
    Returns False if:
    - Simple file operations (no technical keywords)
    - Purely conversational/educational
    - Already handled
    """
    # Check trigger conditions FIRST
    has_install = contains_install(task)
    has_debug = contains_debug(task)
    has_tool = detect_specialized_tool(task) is not None
    is_multistep = is_multi_step(task)
    
    # If any trigger matches, DO lookup (unless clearly conversational)
    if has_install or has_debug or has_tool or is_multistep:
        # Double-check it's not a conversational question about these topics
        task_lower = task.lower()
        if task_lower.startswith(('what is', 'explain', 'define', 'tell me about')):
            # It's a question, not a task - skip lookup
            return False
        return True
    
    # No triggers matched - check if we should skip
    if should_skip(task):
        return False
    
    return False


# ============================================================================
# QUERY GENERATION
# ============================================================================

def extract_keywords(task: str) -> List[str]:
    """Extract relevant keywords from task."""
    task_lower = task.lower()
    keywords = []
    
    # Extract tool names
    tool = detect_specialized_tool(task)
    if tool:
        keywords.append(tool)
    
    # Extract action verbs
    action_verbs = ['install', 'setup', 'configure', 'debug', 'test', 'build', 
                   'deploy', 'create', 'fix', 'troubleshoot', 'process', 'extract']
    
    for verb in action_verbs:
        if verb in task_lower:
            keywords.append(verb)
    
    # Extract technical nouns
    technical_nouns = ['website', 'application', 'video', 'audio', 'database',
                      'api', 'server', 'workflow', 'automation', 'login', 'test']
    
    for noun in technical_nouns:
        if noun in task_lower:
            keywords.append(noun)
    
    # Remove duplicates while preserving order
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw not in seen:
            seen.add(kw)
            unique_keywords.append(kw)
    
    return unique_keywords[:5]  # Limit to 5 keywords


def create_query(task: str) -> str:
    """Create optimized search query from task."""
    keywords = extract_keywords(task)
    return ' '.join(keywords)


def categorize_task(task: str) -> str:
    """Categorize task type."""
    if contains_install(task):
        return 'installation'
    elif contains_debug(task):
        return 'debugging'
    elif detect_specialized_tool(task):
        return f'tool:{detect_specialized_tool(task)}'
    elif is_multi_step(task):
        return 'multi-step'
    else:
        return 'general'


# ============================================================================
# MAIN ROUTER
# ============================================================================

def process_task(task: str, skills_lookup_func=None) -> dict:
    """
    Process task and return skill recommendations.
    
    Args:
        task: User task description
        skills_lookup_func: Function to call skills.lookup (optional)
    
    Returns:
        dict with:
        - should_lookup: bool
        - category: str
        - query: str (if should_lookup)
        - skills: list (if lookup performed)
        - reason: str
    """
    result = {
        'should_lookup': False,
        'category': categorize_task(task),
        'reason': ''
    }
    
    # Check if lookup needed
    if not should_lookup(task):
        result['reason'] = 'Task does not require specialized procedures'
        return result
    
    # Create query
    query = create_query(task)
    result['should_lookup'] = True
    result['query'] = query
    result['reason'] = f'Task detected as {result["category"]}'
    
    # Perform lookup if function provided
    if skills_lookup_func:
        try:
            skills_result = skills_lookup_func(
                query=query,
                task_summary=task,
                max_skills=2,
                search_type='hybrid'
            )
            result['skills'] = skills_result.get('skills', [])
            result['count'] = skills_result.get('count', 0)
        except Exception as e:
            result['error'] = str(e)
    
    return result


# ============================================================================
# TESTS
# ============================================================================

def run_tests():
    """Test router logic."""
    test_cases = [
        # Should trigger
        ("Install Playwright for testing", True, 'installation'),
        ("Debug my FFmpeg video encoding", True, 'debugging'),
        ("Setup n8n workflow automation", True, 'installation'),
        ("Test website with automated scripts", True, 'tool:playwright'),
        ("Download video, extract audio, transcribe", True, 'multi-step'),
        
        # Should NOT trigger
        ("What is Python?", False, 'general'),
        ("Write a poem about coding", False, 'general'),
        ("List files in directory", False, 'general'),
        ("Read this file for me", False, 'general'),
        ("Simple 2+2 calculation", False, 'general'),
    ]
    
    print("🧪 Router Skill Tests")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for task, expected_trigger, expected_category in test_cases:
        should_trigger = should_lookup(task)
        category = categorize_task(task)
        
        if should_trigger == expected_trigger and expected_category in category:
            print(f"✅ PASS: '{task[:40]}...'")
            passed += 1
        else:
            print(f"❌ FAIL: '{task[:40]}...'")
            print(f"   Expected: trigger={expected_trigger}, category={expected_category}")
            print(f"   Got: trigger={should_trigger}, category={category}")
            failed += 1
    
    print("=" * 50)
    print(f"Results: {passed} passed, {failed} failed")
    
    return failed == 0


if __name__ == '__main__':
    success = run_tests()
    exit(0 if success else 1)
