#!/usr/bin/env python3
"""
Skills Scanner - Periodic Discovery of New Unique Skills

Scans external skill repositories, compares against database,
identifies unique/useful skills, performs security checks,
and recommends or auto-imports new skills.

Usage:
    python3 skills_scanner.py [--scan] [--import] [--report] [--cron]

Author: Arty Craftson, Potter's Quill Media
Date: 2026-03-05
"""

import os
import sys
import json
import psycopg2
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Tuple
import hashlib
import re

# Configuration
SKILLS_DB_DSN = os.environ.get('SKILLS_DB_DSN', 'postgresql://localhost:5432/skillsdb')
WORKSPACE = Path.home() / '.openclaw' / 'workspace'
SCANNER_LOG = WORKSPACE / 'logs' / 'skills_scanner.log'
SCANNER_STATE = WORKSPACE / 'skills_scanner_state.json'

# External skill sources to scan
SKILL_SOURCES = {
    'open_skills': {
        'name': 'Open Skills (besoeasy/open-skills)',
        'api_url': 'https://api.github.com/repos/besoeasy/open-skills/contents/skills',
        'raw_url': 'https://raw.githubusercontent.com/besoeasy/open-skills/main/skills/{skill}/SKILL.md',
        'enabled': True
    },
    'anthropic': {
        'name': 'Anthropic Skills',
        'api_url': 'https://api.github.com/repos/anthropics/skills/contents/skills',
        'raw_url': 'https://raw.githubusercontent.com/anthropics/skills/main/skills/{skill}/SKILL.md',
        'enabled': True
    },
    'letta': {
        'name': 'Letta Skills',
        'api_url': 'https://api.github.com/repos/letta-ai/skills/contents/skills',
        'raw_url': 'https://raw.githubusercontent.com/letta-ai/skills/main/skills/{skill}/SKILL.md',
        'enabled': True
    },
    'openai': {
        'name': 'OpenAI Skills',
        'api_url': 'https://api.github.com/repos/openai/skills/contents/skills',
        'raw_url': 'https://raw.githubusercontent.com/openai/skills/main/skills/{skill}/SKILL.md',
        'enabled': False  # Codex-focused, lower priority
    }
}

# Categories we want to prioritize
PRIORITY_CATEGORIES = [
    'communication', 'email', 'messaging', 'telegram', 'slack',
    'automation', 'integration', 'api', 'webhook',
    'security', 'encryption', 'privacy', 'authentication',
    'database', 'sql', 'nosql', 'query',
    'visualization', 'chart', 'graph', 'plot',
    'finance', 'crypto', 'trading', 'investment',
    'productivity', 'task', 'project', 'workflow',
    'ai', 'ml', 'nlp', 'embedding', 'vector',
    'file', 'document', 'pdf', 'image', 'video', 'audio'
]

# Keywords that indicate low-value or duplicate skills
SKIP_KEYWORDS = [
    'test', 'example', 'demo', 'placeholder',
    'todo', 'wip', 'draft', 'deprecated'
]


class SkillsScanner:
    def __init__(self):
        self.db_conn = psycopg2.connect(SKILLS_DB_DSN)
        self.db_conn.autocommit = True
        self.cur = self.db_conn.cursor()
        self.existing_skills = self._load_existing_skills()
        self.new_findings = []
        self.security_issues = []
        
    def _load_existing_skills(self) -> Set[str]:
        """Load existing skill names from database"""
        self.cur.execute("SELECT name FROM skills WHERE status='active'")
        return {row[0].lower() for row in self.cur.fetchall()}
    
    def _load_state(self) -> Dict:
        """Load scanner state from file"""
        if SCANNER_STATE.exists():
            with open(SCANNER_STATE, 'r') as f:
                return json.load(f)
        return {'last_scan': None, 'scanned_skills': []}
    
    def _save_state(self, state: Dict):
        """Save scanner state to file"""
        SCANNER_STATE.parent.mkdir(parents=True, exist_ok=True)
        with open(SCANNER_STATE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def _log(self, message: str, level: str = 'INFO'):
        """Log message to file and console"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] [{level}] {message}"
        print(log_entry)
        
        # Also write to log file
        SCANNER_LOG.parent.mkdir(parents=True, exist_ok=True)
        with open(SCANNER_LOG, 'a') as f:
            f.write(log_entry + '\n')
    
    def _fetch_skill_list(self, source_name: str) -> List[str]:
        """Fetch list of skills from a source"""
        source = SKILL_SOURCES.get(source_name)
        if not source or not source['enabled']:
            return []
        
        try:
            self._log(f"Fetching skills from {source['name']}...")
            response = requests.get(source['api_url'], timeout=30)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list):
                skills = [item['name'] for item in data if item.get('type') == 'dir']
                self._log(f"Found {len(skills)} skills in {source_name}")
                return skills
            else:
                self._log(f"Unexpected response format from {source_name}", 'ERROR')
                return []
                
        except Exception as e:
            self._log(f"Error fetching from {source_name}: {e}", 'ERROR')
            return []
    
    def _fetch_skill_content(self, source_name: str, skill_name: str) -> str:
        """Fetch SKILL.md content for a specific skill"""
        source = SKILL_SOURCES.get(source_name)
        if not source:
            return ''
        
        try:
            url = source['raw_url'].format(skill=skill_name)
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            self._log(f"Error fetching {skill_name}: {e}", 'DEBUG')
            return ''
    
    def _is_skill_unique(self, skill_name: str) -> bool:
        """Check if skill is not already in database"""
        # Normalize name (convert to lowercase, replace underscores with hyphens)
        normalized = skill_name.lower().replace('_', '-')
        return normalized not in self.existing_skills
    
    def _is_skill_useful(self, skill_name: str, content: str) -> bool:
        """Check if skill appears useful (not test/demo/duplicate)"""
        skill_lower = skill_name.lower()
        content_lower = content.lower()
        
        # Skip if contains skip keywords
        for keyword in SKIP_KEYWORDS:
            if keyword in skill_lower or keyword in content_lower[:500]:
                return False
        
        # Check if skill has substantial content
        if len(content) < 200:  # Too short, probably not useful
            return False
        
        # Check if skill has code examples or structured content
        has_code = '```' in content
        has_headers = '#' in content
        has_description = len(content.split('\n')) > 10
        
        return has_code or has_headers or has_description
    
    def _categorize_skill(self, skill_name: str, content: str) -> str:
        """Categorize skill based on name and content"""
        skill_lower = skill_name.lower()
        content_lower = content.lower()
        
        # Check name and content for category keywords
        for category in PRIORITY_CATEGORIES:
            if category in skill_lower or category in content_lower[:1000]:
                return category.title()
        
        return 'General'
    
    def _security_check(self, skill_name: str, content: str) -> Tuple[bool, List[str]]:
        """
        Perform basic security checks on skill content
        Returns: (is_safe, list_of_issues)
        """
        issues = []
        
        # Check for suspicious patterns
        suspicious_patterns = [
            (r'os\.system\s*\(', 'Direct OS command execution'),
            (r'subprocess\.(call|run|Popen)\s*\(', 'Subprocess execution'),
            (r'eval\s*\(', 'Eval usage (code injection risk)'),
            (r'exec\s*\(', 'Exec usage (code injection risk)'),
            (r'__import__\s*\(', 'Dynamic import'),
            (r'pickle\.(load|loads)\s*\(', 'Pickle deserialization (security risk)'),
            (r'yaml\.load\s*\([^)]*\)', 'YAML load without safe_load'),
            (r'requests\.get\s*\([^)]*verify\s*=\s*False', 'Disabling SSL verification'),
        ]
        
        for pattern, description in suspicious_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                issues.append(f"⚠️  {description} detected")
        
        # Check for hardcoded secrets (ADVANCED - skip documentation examples)
        # Only flag if it looks like actual code, not documentation
        secret_patterns = [
            (r'^\s*(password|passwd)\s*=\s*["\'][^"\']+["\']', 'Hardcoded password in code'),
            (r'^\s*(api_key|apikey|API_KEY)\s*=\s*["\'][^"\']+["\']', 'Hardcoded API key in code'),
            (r'^\s*(token|TOKEN)\s*=\s*["\'][^"\']+["\']', 'Hardcoded token in code'),
            (r'^\s*(secret|SECRET)\s*=\s*["\'][^"\']+["\']', 'Hardcoded secret in code'),
            (r'^\s*(private_key|PRIVATE_KEY)\s*=\s*["\'][^"\']+["\']', 'Hardcoded private key'),
            (r'^\s*(access_token|AUTH_TOKEN)\s*=\s*["\'][^"\']+["\']', 'Hardcoded access/auth token'),
        ]
        
        # Check line-by-line to avoid matching documentation examples
        for line in content.split('\n'):
            # Skip comment lines and markdown
            if line.strip().startswith('#') or line.strip().startswith('//'):
                continue
            if line.strip().startswith('```') or line.strip().startswith('**'):
                continue
            if 'example' in line.lower() or 'demo' in line.lower():
                continue
            
            # Check for actual code assignments
            for pattern, description in secret_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    # Double-check: is this inside a code block?
                    if '```' in content:
                        # Check if this line is likely example code
                        if 'your-' in line.lower() or 'xxx' in line.lower() or 'example' in line.lower():
                            continue  # Skip obvious examples
                    issues.append(f"⚠️  {description} detected")
        
        # Remove duplicates
        issues = list(set(issues))
        
        # Check for network calls without error handling
        if 'requests.' in content or 'urllib' in content:
            if 'try:' not in content or 'except' not in content:
                issues.append("⚠️  Network calls without error handling")
        
        # Check if skill uses environment variables (good practice)
        uses_env_vars = bool(re.search(r'os\.environ\.get|os\.getenv|\$\{|process\.env', content))
        if not uses_env_vars and any('secret' in i.lower() or 'password' in i.lower() or 'key' in i.lower() for i in issues):
            issues.append("💡 Recommendation: Use environment variables instead of hardcoded values")
        
        is_safe = len([i for i in issues if not i.startswith('💡')]) == 0
        return is_safe, issues
    
    def _calculate_priority_score(self, skill_name: str, content: str, category: str) -> float:
        """Calculate priority score for importing skill"""
        score = 0.0
        
        # Category priority (higher for priority categories)
        if category.lower() in [c.lower() for c in PRIORITY_CATEGORIES[:10]]:
            score += 30.0
        elif category.lower() in [c.lower() for c in PRIORITY_CATEGORIES]:
            score += 20.0
        else:
            score += 10.0
        
        # Content quality
        if len(content) > 500:
            score += 10.0
        if '```' in content:
            score += 15.0  # Has code examples
        if content.count('#') > 3:
            score += 10.0  # Well structured
        
        # Security (no issues = higher score)
        is_safe, _ = self._security_check(skill_name, content)
        if is_safe:
            score += 20.0
        
        # Uniqueness bonus
        if self._is_skill_unique(skill_name):
            score += 15.0
        
        return score
    
    def scan(self, sources: List[str] = None) -> Dict:
        """
        Scan skill sources for new unique skills
        Returns: Dictionary of findings
        """
        self._log("=" * 70)
        self._log("SKILLS SCANNER - Starting Scan")
        self._log("=" * 70)
        
        if sources is None:
            sources = [s for s, config in SKILL_SOURCES.items() if config['enabled']]
        
        state = self._load_state()
        all_new_skills = []
        
        for source in sources:
            self._log(f"\nScanning {SKILL_SOURCES[source]['name']}...")
            skill_list = self._fetch_skill_list(source)
            
            for skill_name in skill_list:
                # Skip if already scanned recently
                if skill_name in state.get('scanned_skills', []):
                    continue
                
                # Check if unique
                if not self._is_skill_unique(skill_name):
                    self._log(f"  ⏭️  {skill_name} - Already in database", 'DEBUG')
                    continue
                
                # Fetch content
                content = self._fetch_skill_content(source, skill_name)
                if not content:
                    continue
                
                # Check if useful
                if not self._is_skill_useful(skill_name, content):
                    self._log(f"  ⏭️  {skill_name} - Not useful", 'DEBUG')
                    continue
                
                # Categorize
                category = self._categorize_skill(skill_name, content)
                
                # Security check
                is_safe, security_issues = self._security_check(skill_name, content)
                
                # Calculate priority
                priority_score = self._calculate_priority_score(skill_name, content, category)
                
                # Add to findings
                finding = {
                    'name': skill_name,
                    'source': source,
                    'category': category,
                    'content_length': len(content),
                    'is_safe': is_safe,
                    'security_issues': security_issues,
                    'priority_score': priority_score,
                    'content': content,
                    'scanned_at': datetime.now().isoformat()
                }
                
                all_new_skills.append(finding)
                state.setdefault('scanned_skills', []).append(skill_name)
                
                # Log finding
                status = "✅" if is_safe else "⚠️ "
                self._log(f"  {status} {skill_name} - {category} (Score: {priority_score:.1f})")
                
                if security_issues:
                    for issue in security_issues:
                        self._log(f"      {issue}", 'WARNING')
        
        # Sort by priority score
        all_new_skills.sort(key=lambda x: x['priority_score'], reverse=True)
        
        # Save state
        state['last_scan'] = datetime.now().isoformat()
        self._save_state(state)
        
        self.new_findings = all_new_skills
        
        # Summary
        self._log("\n" + "=" * 70)
        self._log(f"SCAN COMPLETE - Found {len(all_new_skills)} new unique skills")
        self._log("=" * 70)
        
        return {
            'total_found': len(all_new_skills),
            'safe_skills': len([s for s in all_new_skills if s['is_safe']]),
            'skills_with_issues': len([s for s in all_new_skills if not s['is_safe']]),
            'by_category': self._group_by_category(all_new_skills),
            'top_recommendations': all_new_skills[:10],  # Top 10 by priority
            'findings': all_new_skills
        }
    
    def _group_by_category(self, skills: List[Dict]) -> Dict[str, int]:
        """Group skills by category"""
        categories = {}
        for skill in skills:
            cat = skill['category']
            categories[cat] = categories.get(cat, 0) + 1
        return categories
    
    def generate_report(self, output_file: str = None) -> str:
        """Generate human-readable report of findings"""
        if not self.new_findings:
            return "No new skills found in last scan. Run scan() first."
        
        report = []
        report.append("=" * 70)
        report.append("SKILLS SCANNER - DISCOVERY REPORT")
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S EST')}")
        report.append("=" * 70)
        report.append("")
        
        # Summary
        safe_count = len([s for s in self.new_findings if s['is_safe']])
        report.append(f"Total New Skills Found: {len(self.new_findings)}")
        report.append(f"✅ Safe to Import: {safe_count}")
        report.append(f"⚠️  Security Review Needed: {len(self.new_findings) - safe_count}")
        report.append("")
        
        # By category
        report.append("By Category:")
        by_cat = self._group_by_category(self.new_findings)
        for cat, count in sorted(by_cat.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {cat}: {count}")
        report.append("")
        
        # Top recommendations
        report.append("🎯 TOP RECOMMENDATIONS (Priority Score > 50):")
        report.append("-" * 70)
        for i, skill in enumerate(self.new_findings[:10], 1):
            if skill['priority_score'] >= 50:
                status = "✅" if skill['is_safe'] else "⚠️ "
                report.append(f"{i}. {status} {skill['name']}")
                report.append(f"   Source: {skill['source']} | Category: {skill['category']}")
                report.append(f"   Priority Score: {skill['priority_score']:.1f}")
                if skill['security_issues']:
                    report.append(f"   Security Issues: {', '.join(skill['security_issues'])}")
                report.append("")
        
        # Skills needing security review
        unsafe_skills = [s for s in self.new_findings if not s['is_safe']]
        if unsafe_skills:
            report.append("")
            report.append("🔒 SKILLS NEEDING SECURITY REVIEW:")
            report.append("-" * 70)
            for skill in unsafe_skills:
                report.append(f"⚠️  {skill['name']}")
                for issue in skill['security_issues']:
                    report.append(f"    - {issue}")
                report.append("")
        
        report.append("=" * 70)
        
        report_text = '\n'.join(report)
        
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report_text)
            self._log(f"Report saved to {output_file}")
        
        return report_text
    
    def import_skill(self, skill_name: str, auto_approve: bool = False) -> bool:
        """Import a single skill to database"""
        finding = next((s for s in self.new_findings if s['name'] == skill_name), None)
        
        if not finding:
            self._log(f"Skill {skill_name} not found in scan results", 'ERROR')
            return False
        
        # Security check
        if not finding['is_safe'] and not auto_approve:
            self._log(f"Skill {skill_name} has security issues. Review required.", 'WARNING')
            self._log("Security Issues:")
            for issue in finding['security_issues']:
                self._log(f"  - {issue}")
            response = input("Import anyway? (y/N): ")
            if response.lower() != 'y':
                return False
        
        # Import using existing import script
        import_script = WORKSPACE / 'repos' / 'openclaw-dymanic-skills-system' / 'scripts' / 'import_skill.py'
        
        if not import_script.exists():
            self._log("Import script not found!", 'ERROR')
            return False
        
        # Create temporary file with skill content
        temp_dir = WORKSPACE / 'temp_skills'
        temp_dir.mkdir(parents=True, exist_ok=True)
        temp_file = temp_dir / f"{skill_name}_SKILL.md"
        
        with open(temp_file, 'w') as f:
            f.write(finding['content'])
        
        # Run import script
        import subprocess
        try:
            result = subprocess.run(
                ['python3', str(import_script), str(temp_file)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                self._log(f"✅ Successfully imported {skill_name}")
                # Clean up
                temp_file.unlink()
                return True
            else:
                self._log(f"❌ Import failed: {result.stderr}", 'ERROR')
                return False
                
        except Exception as e:
            self._log(f"❌ Import error: {e}", 'ERROR')
            return False
    
    def import_top_skills(self, limit: int = 5, auto_approve: bool = False):
        """Import top N safe skills automatically"""
        self._log(f"\nImporting top {limit} safe skills...")
        
        safe_skills = [s for s in self.new_findings if s['is_safe']]
        imported = 0
        
        for skill in safe_skills[:limit]:
            if self.import_skill(skill['name'], auto_approve):
                imported += 1
        
        self._log(f"Imported {imported}/{limit} skills")
        return imported


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Skills Scanner - Discover new unique skills')
    parser.add_argument('--scan', action='store_true', help='Scan for new skills')
    parser.add_argument('--import', dest='do_import', action='store_true', help='Import top skills')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--cron', action='store_true', help='Run in cron mode (scan + report)')
    parser.add_argument('--limit', type=int, default=5, help='Number of skills to import')
    parser.add_argument('--auto-approve', action='store_true', help='Skip security prompts')
    parser.add_argument('--output', type=str, help='Output file for report')
    
    args = parser.parse_args()
    
    scanner = SkillsScanner()
    
    if args.scan or args.cron:
        results = scanner.scan()
        print(f"\nFound {results['total_found']} new skills")
        print(f"Safe: {results['safe_skills']} | Needs Review: {results['skills_with_issues']}")
    
    if args.report or args.cron:
        report = scanner.generate_report(args.output)
        print("\n" + report)
    
    if args.do_import:
        scanner.import_top_skills(args.limit, args.auto_approve)
    
    if not any([args.scan, args.do_import, args.report, args.cron]):
        parser.print_help()


if __name__ == '__main__':
    main()
