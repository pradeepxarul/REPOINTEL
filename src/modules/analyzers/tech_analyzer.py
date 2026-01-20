"""
Technology Stack Analyzer Module

Analyzes programming languages, frameworks, and libraries used in repositories.
"""
import re
from typing import Dict, List
from collections import Counter
from datetime import datetime
from utils.logger import logger
from config.keywords_config import get_tech_categories, get_all_keywords_flat
from modules.analyzers.dependency_parser import dependency_parser


class TechAnalyzer:
    """
    Analyzes technology stack from repository data.
    
    Features:
    - Language distribution analysis
    - Framework/library detection
    - Primary/secondary stack identification
    - Recent usage tracking
    """
    
    def __init__(self):
        """Initialize analyzer with technology keywords."""
        self.tech_categories = get_tech_categories()
        self.all_tech_keywords = get_all_keywords_flat()
        logger.info(f"[TOOL] Tech Analyzer initialized with {len(self.all_tech_keywords)} keywords")
    
    def analyze_technologies(self, repos: List[Dict], language_distribution: Dict[str, float]) -> Dict:
        """
        Analyze technology stack from repositories.
        
        Args:
            repos: List of repository data
            language_distribution: Dict of language -> percentage
            
        Returns:
            Dict with technologies, primary_stack, secondary_stack, technology_summary
        """
        technologies = []
        sorted_langs = sorted(language_distribution.items(), key=lambda x: x[1], reverse=True)
        
        primary = []
        secondary = []
        
        for lang, pct in sorted_langs:
            relevant_repos = self._find_repos_with_language(repos, lang)
            count = len(relevant_repos)
            recent = self._has_recent_usage(repos, relevant_repos)
            
            technologies.append({
                "name": lang,
                "category": "language",
                "usage_percentage": round(pct, 1),
                "repository_count": count,
                "recent_usage": recent,
                "example_repositories": relevant_repos[:4]
            })
            
            if pct > 15:
                primary.append(lang)
            else:
                secondary.append(lang)
        
        return {
            "technologies": technologies,
            "primary_stack": primary[:3],
            "secondary_stack": secondary[:5],
            "technology_summary": self._generate_summary(primary)
        }
    
    def detect_frameworks(self, repos: List[Dict], parsed_dependencies: List[Dict] = None) -> List[Dict]:
        """
        Detect frameworks and libraries across repositories.
        
        Args:
            repos: List of repository data
            parsed_dependencies: Optional list of parsed dependencies from manifest files
            
        Returns:
            List of detected frameworks with evidence (enriched with versions if available)
        """
        fw_counts = Counter()
        fw_evidence = {}
        
        for repo in repos:
            text = self._prepare_text(repo)
            
            for keyword, category in self.all_tech_keywords.items():
                if self._keyword_matches(keyword, text):
                    fw_counts[keyword] += 1
                    if keyword not in fw_evidence:
                        fw_evidence[keyword] = {"repo": repo['name'], "cat": category}
        
        frameworks = []
        for keyword, count in fw_counts.most_common(25):
            formatted_name = keyword.title()
            category = fw_evidence[keyword]["cat"]
            
            framework = {
                "name": formatted_name,
                "category": category,
                "evidence": f"Detected in {count} repositories including {fw_evidence[keyword]['repo']}"
            }
            
            frameworks.append(framework)
        
        # Enrich with dependency versions if available
        if parsed_dependencies:
            frameworks = self.enrich_with_dependencies(frameworks, parsed_dependencies)
        
        return frameworks
    
    def enrich_with_dependencies(self, detected_frameworks: List[Dict], parsed_dependencies: List[Dict]) -> List[Dict]:
        """
        Enrich detected frameworks with exact versions from parsed dependencies.
        
        Args:
            detected_frameworks: Frameworks detected via keyword matching
            parsed_dependencies: Dependencies parsed from manifest files
            
        Returns:
            Enriched frameworks list with version information where available
        """
        # Create lookup dict from parsed dependencies (lowercase name -> dependency)
        dep_lookup = {}
        for dep in parsed_dependencies:
            dep_name_lower = dep['name'].lower()
            dep_lookup[dep_name_lower] = dep
        
        # Enrich frameworks with version info
        enriched = []
        for fw in detected_frameworks:
            fw_name_lower = fw['name'].lower()
            
            # Check for exact match or partial match
            matched_dep = None
            if fw_name_lower in dep_lookup:
                matched_dep = dep_lookup[fw_name_lower]
            else:
                # Try partial match (e.g., "react" matches "react-dom")
                for dep_name, dep in dep_lookup.items():
                    if fw_name_lower in dep_name or dep_name in fw_name_lower:
                        matched_dep = dep
                        break
            
            if matched_dep:
                # Add version info from manifest file
                fw['version'] = matched_dep['version']
                fw['exact_match'] = True
                fw['evidence'] = f"{matched_dep['source_file']} in repository"
            
            enriched.append(fw)
        
        # Add dependencies that weren't detected by keywords (e.g., less common libraries)
        detected_names = {fw['name'].lower() for fw in enriched}
        for dep in parsed_dependencies:
            if dep['name'].lower() not in detected_names and dep['type'] == 'dependency':
                # Add as new framework entry
                enriched.append({
                    "name": dep['name'].title(),
                    "version": dep['version'],
                    "category": self._infer_category(dep['name'], dep['ecosystem']),
                    "evidence": f"{dep['source_file']} in repository",
                    "exact_match": True
                })
        
        return enriched
    
    def _find_repos_with_language(self, repos: List[Dict], language: str) -> List[str]:
        """Find repository names that use a specific language."""
        return [
            r['name'] for r in repos 
            if r.get('languages', {}).get('percentages', {}).get(language, 0) > 0
        ]
    
    def _has_recent_usage(self, repos: List[Dict], repo_names: List[str]) -> bool:
        """Check if any of the repos have been updated in last 180 days."""
        for repo in repos:
            if repo.get('name') in repo_names:
                pushed = repo.get('pushed_at')
                if pushed:
                    dt = datetime.fromisoformat(pushed.replace("Z", "+00:00")).replace(tzinfo=None)
                    if (datetime.utcnow() - dt).days < 180:
                        return True
        return False
    
    def _prepare_text(self, repo: Dict) -> str:
        """Prepare searchable text from repository data."""
        description = repo.get('description') or ""
        topics = " ".join(repo.get('topics') or [])
        return (description + " " + topics).lower()
    
    def _keyword_matches(self, keyword: str, text: str) -> bool:
        """Check if keyword matches in text with appropriate matching strategy."""
        if len(keyword) < 4:
            # Short keywords need word boundary
            return bool(re.search(r'\b' + re.escape(keyword) + r'\b', text))
        else:
            # Longer keywords use substring match
            return keyword in text
    
    def _generate_summary(self, primary_langs: List[str]) -> str:
        """Generate technology summary text."""
        if not primary_langs:
            return "Developer"
        return f"Full-stack developer with {', '.join(primary_langs[:2])} expertise"
    
    def _infer_category(self, dep_name: str, ecosystem: str) -> str:
        """
        Infer framework category based on dependency name and ecosystem.
        
        Args:
            dep_name: Dependency name
            ecosystem: Package ecosystem (npm, pip, etc.)
            
        Returns:
            Inferred category string
        """
        dep_lower = dep_name.lower()
        
        # Frontend frameworks
        if any(x in dep_lower for x in ['react', 'vue', 'angular', 'svelte', 'next', 'nuxt']):
            return "Frontend Framework"
        
        # Backend frameworks
        if any(x in dep_lower for x in ['express', 'fastapi', 'django', 'flask', 'nest', 'koa']):
            return "Backend Framework"
        
        # Testing
        if any(x in dep_lower for x in ['jest', 'pytest', 'mocha', 'chai', 'vitest']):
            return "Testing Framework"
        
        # Database
        if any(x in dep_lower for x in ['mongo', 'postgres', 'mysql', 'redis', 'prisma', 'sequelize']):
            return "Database"
        
        # Default based on ecosystem
        if ecosystem == 'npm':
            return "JavaScript Library"
        elif ecosystem == 'pip':
            return "Python Library"
        elif ecosystem == 'go':
            return "Go Module"
        else:
            return "Library"


# Singleton instance
tech_analyzer = TechAnalyzer()
