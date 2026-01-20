"""
Scoring Engine Module

Calculates metrics and scores for GitHub profiles.
"""
from typing import Dict, List
from datetime import datetime, timedelta
from collections import Counter
from utils.logger import logger


class ScoringEngine:
    """
    Calculates various metrics and scores for developer assessment.
    
    Features:
    - Raw metrics calculation (stars, forks, activity)
    - Quality scoring
    - Consistency scoring
    - Technical depth assessment
    """
    
    def __init__(self):
        """Initialize scoring engine."""
        logger.info("[STATS] Scoring Engine initialized")
    
    def calculate_metrics(self, user: Dict, repos: List[Dict]) -> Dict:
        """
        Calculate raw numerical metrics from user and repository data.
        
        Args:
            user: User profile data
            repos: List of repository data
            
        Returns:
            Dict with all calculated metrics
        """
        total_repos = len(repos)
        if total_repos == 0:
            return self._get_empty_metrics()
        
        # Basic counts
        total_stars = sum(r.get("stargazers_count", 0) for r in repos)
        total_forks = sum(r.get("forks_count", 0) for r in repos)
        repos_with_readme = sum(1 for r in repos if r.get("readme"))
        
        # Language distribution
        lang_bytes = Counter()
        for repo in repos:
            langs = repo.get("languages", {}).get("raw_bytes", {})
            if langs:
                lang_bytes.update(langs)
        
        total_bytes = sum(lang_bytes.values())
        lang_distribution = {
            k: (v / total_bytes * 100) for k, v in lang_bytes.items()
        } if total_bytes > 0 else {}
        
        # Activity metrics
        now = datetime.utcnow()
        commits = []
        for repo in repos:
            pushed_at = repo.get("pushed_at") or repo.get("updated_at")
            if pushed_at:
                dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00")).replace(tzinfo=None)
                commits.append(dt)
        
        last_commit = max(commits) if commits else now - timedelta(days=365)
        days_since = (now - last_commit).days
        active_repos = sum(1 for d in commits if (now - d).days < 90)
        
        # Production signals
        has_prod = any(
            "production" in (r.get('description') or "").lower() or
            "deploy" in (r.get('description') or "").lower() or
            "workflow" in (r.get('description') or "").lower()
            for r in repos
        )
        
        # Account age
        created_at = user.get("created_at", "")
        account_age = 0
        if created_at:
            created_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")).replace(tzinfo=None)
            account_age = (now - created_dt).days / 365.25
        
        return {
            "total_repos": total_repos,
            "total_stars": total_stars,
            "total_forks": total_forks,
            "repos_with_readme": repos_with_readme,
            "documentation_percentage": (repos_with_readme / total_repos) * 100,
            "total_markdown_files": sum(len(r.get("markdown_files", [])) for r in repos),
            "days_since_last_commit": days_since,
            "active_repos_count": active_repos,
            "account_age_years": round(account_age, 1),
            "language_distribution": lang_distribution,
            "has_production_signals": has_prod
        }
    
    def calculate_scores(self, metrics: Dict, tech_analysis: Dict) -> Dict:
        """
        Calculate quality and assessment scores.
        
        Args:
            metrics: Raw metrics from calculate_metrics
            tech_analysis: Technology analysis results
            
        Returns:
            Dict with all calculated scores
        """
        # Consistency score based on recent activity
        days = metrics['days_since_last_commit']
        if days < 7:
            const_score = 10
        elif days < 30:
            const_score = 8
        elif days < 90:
            const_score = 6
        else:
            const_score = 3
        
        # Documentation score
        doc_score = min(10, round(metrics['documentation_percentage'] / 10))
        
        # Star-based quality score
        star_raw = metrics['total_stars']
        star_score = min(10, star_raw // 5)  # 50 stars = 10/10
        
        # Overall score (weighted average)
        overall = (star_score * 0.3) + (const_score * 0.3) + (doc_score * 0.4)
        overall = round(max(6.0, overall), 1)
        
        # Proficiency mapping for primary languages
        proficiency = {}
        for lang in tech_analysis.get('primary_stack', []):
            proficiency[lang] = {"score": 8, "evidence": "Primary language"}
        
        # Technical depth assessment
        if overall > 8.5:
            depth = "Senior"
        elif overall > 6.5:
            depth = "Mid-level"
        else:
            depth = "Junior"
        
        # Activity label
        activity_label = "High Volume" if metrics['active_repos_count'] > 3 else "Standard"
        
        return {
            "overall": overall,
            "consistency": const_score,
            "docs_score": doc_score,
            "depth": depth,
            "proficiency": proficiency,
            "trajectory": "Rising" if const_score > 7 else "Steady",
            "quality": round((doc_score + 8) / 2, 1),
            "activity_label": activity_label
        }
    
    def _get_empty_metrics(self) -> Dict:
        """Return empty metrics for users with no repositories."""
        return {
            "total_repos": 0,
            "total_stars": 0,
            "total_forks": 0,
            "repos_with_readme": 0,
            "documentation_percentage": 0,
            "total_markdown_files": 0,
            "days_since_last_commit": 999,
            "active_repos_count": 0,
            "account_age_years": 0,
            "language_distribution": {},
            "has_production_signals": False
        }


# Singleton instance
scoring_engine = ScoringEngine()
