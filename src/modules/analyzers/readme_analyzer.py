"""
README Analyzer Module

Extracts technical skills, technologies, frameworks, and tools from README content
using pattern matching and keyword detection.
"""

import re
from typing import Dict, List, Set, Optional
from dataclasses import dataclass


@dataclass
class ExtractedSkill:
    """Represents a skill extracted from README"""
    name: str
    category: str
    source: str  # 'package_manager', 'import', 'keyword', 'badge', 'code_block'
    version: Optional[str] = None
    confidence: float = 1.0


class ReadmeAnalyzer:
    """Analyzes README content to extract technical skills"""
    
    def __init__(self):
        """Initialize the README analyzer with extraction patterns"""
        
        # Package manager patterns
        self.package_patterns = {
            'npm': r'npm\s+install\s+(?:--save(?:-dev)?\s+)?([a-z0-9@\-/]+(?:\s+[a-z0-9@\-/]+)*)',
            'pip': r'pip\s+install\s+([a-z0-9\-_]+(?:\s+[a-z0-9\-_]+)*)',
            'gem': r'gem\s+install\s+([a-z0-9\-_]+(?:\s+[a-z0-9\-_]+)*)',
            'go': r'go\s+get\s+([a-z0-9\-_/.]+)',
            'composer': r'composer\s+require\s+([a-z0-9\-_/]+(?:\s+[a-z0-9\-_/]+)*)',
            'cargo': r'cargo\s+add\s+([a-z0-9\-_]+(?:\s+[a-z0-9\-_]+)*)',
            'yarn': r'yarn\s+add\s+([a-z0-9@\-/]+(?:\s+[a-z0-9@\-/]+)*)',
        }
        
        # Import statement patterns
        self.import_patterns = {
            'javascript': r'import\s+.*?\s+from\s+[\'"]([a-z0-9@\-/]+)[\'"]',
            'python': r'(?:from\s+([a-z0-9_]+)|import\s+([a-z0-9_]+))',
            'java': r'import\s+([a-z0-9_.]+)',
            'go': r'import\s+[\'"]([a-z0-9\-_/.]+)[\'"]',
            'php': r'use\s+([a-z0-9_\\\\]+)',
        }
        
        # Badge patterns
        self.badge_pattern = r'\[!\[([^\]]+)\]\(([^\)]+)\)\]\(([^\)]+)\)'
        
        # Code block pattern
        self.code_block_pattern = r'```(\w+)\n(.*?)```'
        
        # Technology keyword patterns (case-insensitive)
        self.tech_keywords = self._build_tech_keywords()
        
        # Stopwords to filter out false positives
        self.stopwords = self._build_stopwords()
        
    def _build_tech_keywords(self) -> Dict[str, Set[str]]:
        """Build comprehensive technology keyword dictionary"""
        keywords = {
            'frameworks': {
                'react', 'vue', 'angular', 'django', 'flask', 'fastapi', 'express',
                'spring', 'laravel', 'rails', 'nextjs', 'nuxt', 'gatsby', 'nest',
                'svelte', 'ember', 'backbone', 'meteor', 'koa', 'hapi', 'sails',
                'adonis', 'strapi', 'feathers', 'loopback', 'redux', 'mobx',
                'vuex', 'rxjs', 'jquery', 'bootstrap', 'tailwind', 'material-ui',
                'ant-design', 'chakra-ui', 'semantic-ui'
            },
            'databases': {
                'postgresql', 'mysql', 'mongodb', 'redis', 'elasticsearch',
                'cassandra', 'dynamodb', 'sqlite', 'mariadb', 'oracle',
                'mssql', 'couchdb', 'neo4j', 'influxdb', 'firebase',
                'supabase', 'planetscale', 'cockroachdb', 'timescaledb'
            },
            'tools': {
                'docker', 'kubernetes', 'jenkins', 'travis', 'circleci',
                'github actions', 'gitlab ci', 'webpack', 'babel', 'eslint',
                'prettier', 'jest', 'pytest', 'mocha', 'chai', 'cypress',
                'selenium', 'playwright', 'puppeteer', 'vite', 'rollup',
                'parcel', 'grunt', 'gulp', 'terraform', 'ansible', 'vagrant',
                'nginx', 'apache', 'pm2', 'nodemon'
            },
            'languages': {
                'javascript', 'typescript', 'python', 'java', 'csharp', 'cpp',
                'go', 'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala',
                'dart', 'elixir', 'clojure', 'haskell', 'r', 'matlab'
            },
        }
        
        return keywords
    
    def _build_stopwords(self) -> Set[str]:
        """Build comprehensive stopwords list to filter false positives"""
        return {
            # Common English words
            'the', 'a', 'an', 'and', 'or', 'but', 'if', 'then', 'else', 'when',
            'at', 'from', 'into', 'during', 'including', 'until', 'against', 'among',
            'throughout', 'despite', 'towards', 'upon', 'of', 'for', 'on', 'in',
            'to', 'as', 'by', 'with', 'about', 'like', 'through', 'over', 'before',
            'after', 'above', 'below', 'up', 'down', 'out', 'off', 'within',
            
            # Common verbs/adjectives
            'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had',
            'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might',
            'must', 'can', 'shall', 'get', 'set', 'make', 'take', 'use', 'used',
            'using', 'one', 'two', 'first', 'last', 'new', 'old', 'good', 'bad',
            
            # Generic programming/tech terms (not frameworks!)
            'requirements', 'requirement', 'install', 'installation', 'setup',
            'config', 'configuration', 'settings', 'options', 'example', 'examples',
            'test', 'tests', 'testing', 'build', 'builds', 'run', 'running',
            'start', 'stop', 'restart', 'dev', 'development', 'prod', 'production',
            'env', 'environment', 'var', 'variable', 'path', 'file', 'files',
            'folder', 'directory', 'src', 'source', 'dist', 'output', 'input',
            'app', 'application', 'server', 'client', 'api', 'endpoint', 'route',
            'package', 'packages', 'module', 'modules', 'lib', 'library', 'libraries',
            'node', 'npm', 'pip', 'gem', 'cargo', 'composer', 'yarn', 'pnpm',
            'version', 'versions', 'update', 'upgrade', 'latest', 'stable',
            
            # Common placeholder variable names
            'foo', 'bar', 'baz', 'qux', 'temp', 'tmp', 'data', 'value', 'item',
            'obj', 'object', 'arr', 'array', 'list', 'dict', 'map', 'key', 'val',
            
            # Documentation/README specific
            'readme', 'license', 'contributing', 'changelog', 'todo', 'note',
            'notes', 'docs', 'documentation', 'guide', 'tutorial', 'getting',
            'started', 'quick', 'quickstart', 'introduction', 'overview',
        }
    
    def analyze_readme(self, readme_content: str) -> List[ExtractedSkill]:
        """
        Analyze README content and extract all technical skills
        
        Args:
            readme_content: The README file content
            
        Returns:
            List of ExtractedSkill objects
        """
        if not readme_content:
            return []
        
        skills = []
        
        # Extract from package managers
        skills.extend(self._extract_from_packages(readme_content))
        
        # Extract from import statements
        skills.extend(self._extract_from_imports(readme_content))
        
        # Extract from badges
        skills.extend(self._extract_from_badges(readme_content))
        
        # Extract from code blocks
        skills.extend(self._extract_from_code_blocks(readme_content))
        
        # Extract from technology keywords
        skills.extend(self._extract_from_keywords(readme_content))
        
        # Deduplicate and merge
        return self._deduplicate_skills(skills)
    
    def _extract_from_packages(self, content: str) -> List[ExtractedSkill]:
        """Extract skills from package manager commands"""
        skills = []
        
        for pm, pattern in self.package_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                packages = match.group(1).split()
                for package in packages:
                    # Clean package name
                    package = package.strip().split('@')[0].split('/')[-1].strip()
                    package_lower = package.lower()
                    
                    # FILTER OUT stopwords (case-insensitive) and invalid names
                    # Must be 3+ chars, alphanumeric, and contain at least one letter
                    if (package_lower not in self.stopwords and 
                        len(package_lower) >= 3 and
                        package_lower.replace('_', '').replace('-', '').isalnum() and
                        any(c.isalpha() for c in package_lower)):
                        
                        skills.append(ExtractedSkill(
                            name=package.capitalize(),
                            category='library',
                            source='package_manager',
                            confidence=0.9
                        ))
        
        return skills
    
    def _extract_from_imports(self, content: str) -> List[ExtractedSkill]:
        """Extract skills from import statements in code blocks"""
        skills = []
        
        # Python: import X, from X import Y
        # JS: import X from 'Y', const X = require('Y')
        import_patterns = {
            'python': r'(?:^|\n)(?:from\s+([a-zA-Z0-9_.-]+)|import\s+([a-zA-Z0-9_.-]+))',
            'javascript': r"(?:import.*?from\s+['\"]([^'\"]+)['\"]|require\(['\"]([^'\"]+)['\"]\))"
        }
        
        for lang, pattern in import_patterns.items():
            matches = re.finditer(pattern, content, re.MULTILINE | re.IGNORECASE)
            for match in matches:
                module = match.group(1) or match.group(2) if match.lastindex >= 2 else match.group(1)
                if module:
                    # Clean module name
                    module = module.split('.')[0].split('/')[0].strip()
                    module_lower = module.lower()
                    
                    # FILTER OUT (case-insensitive):
                    # 1. Stopwords (common English words like "this", "the", etc.)
                    # 2. Too short (< 3 chars)
                    # 3. Not alphanumeric (after removing - and _)
                    # 4. Must contain at least one letter (not just numbers like "123")
                    if (module_lower not in self.stopwords and 
                        len(module_lower) >= 3 and
                        module_lower.replace('_', '').replace('-', '').isalnum() and
                        any(c.isalpha() for c in module_lower)):
                        
                        skills.append(ExtractedSkill(
                            name=module.capitalize(),
                            category='library',
                            source='import',
                            confidence=0.8
                        ))
        
        return skills
    
    def _extract_from_badges(self, content: str) -> List[ExtractedSkill]:
        """Extract skills from README badges"""
        skills = []
        
        matches = re.finditer(self.badge_pattern, content)
        for match in matches:
            badge_text = match.group(1).lower()
            badge_url = match.group(2).lower()
            
            # CI/CD tools
            ci_tools = ['travis', 'circleci', 'jenkins', 'github actions', 'gitlab ci', 'azure pipelines']
            for tool in ci_tools:
                if tool in badge_text or tool in badge_url:
                    skills.append(ExtractedSkill(
                        name=tool.title(),
                        category='tool',
                        source='badge',
                        confidence=0.95
                    ))
            
            # Testing/Coverage
            if 'coverage' in badge_text or 'codecov' in badge_url:
                skills.append(ExtractedSkill(
                    name='Code Coverage',
                    category='practice',
                    source='badge',
                    confidence=0.9
                ))
        
        return skills
    
    def _extract_from_code_blocks(self, content: str) -> List[ExtractedSkill]:
        """Extract programming languages from code blocks"""
        skills = []
        
        matches = re.finditer(self.code_block_pattern, content, re.DOTALL)
        seen_languages = set()
        
        for match in matches:
            language = match.group(1).lower()
            if language and language not in seen_languages:
                # Map common aliases
                lang_map = {
                    'js': 'javascript',
                    'ts': 'typescript',
                    'py': 'python',
                    'rb': 'ruby',
                    'sh': 'shell',
                    'bash': 'shell',
                }
                language = lang_map.get(language, language)
                
                skills.append(ExtractedSkill(
                    name=language.capitalize(),
                    category='language',
                    source='code_block',
                    confidence=0.8
                ))
                seen_languages.add(language)
        
        return skills
    
    def _extract_from_keywords(self, content: str) -> List[ExtractedSkill]:
        """Extract skills from technology keyword mentions"""
        skills = []
        content_lower = content.lower()
        
        # Search for each category
        for category, keywords in self.tech_keywords.items():
            for keyword in keywords:
                # Use word boundaries to avoid partial matches
                pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
                if re.search(pattern, content_lower):
                    skills.append(ExtractedSkill(
                        name=keyword.title(),
                        category=category.rstrip('s'),  # 'frameworks' -> 'framework'
                        source='keyword',
                        confidence=0.7
                    ))
        
        return skills
    
    def _deduplicate_skills(self, skills: List[ExtractedSkill]) -> List[ExtractedSkill]:
        """Deduplicate skills and keep highest confidence"""
        skill_map = {}
        
        for skill in skills:
            key = skill.name.lower()
            if key not in skill_map or skill.confidence > skill_map[key].confidence:
                skill_map[key] = skill
        
        return list(skill_map.values())
    
    def get_skill_summary(self, skills: List[ExtractedSkill]) -> Dict[str, List[str]]:
        """
        Get a summary of extracted skills grouped by category
        
        Args:
            skills: List of ExtractedSkill objects
            
        Returns:
            Dictionary with categories as keys and skill names as values
        """
        summary = {}
        
        for skill in skills:
            if skill.category not in summary:
                summary[skill.category] = []
            summary[skill.category].append(skill.name)
        
        # Sort each category
        for category in summary:
            summary[category] = sorted(set(summary[category]))
        
        return summary


# Singleton instance
readme_analyzer = ReadmeAnalyzer()
