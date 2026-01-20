"""
Domain Classification Module

Handles domain detection and weighted scoring for GitHub repositories.
Uses keyword matching with configurable weights to prioritize specialized domains.
"""
import re
from typing import Dict, List, Tuple
from collections import Counter
from utils.logger import logger
from config.keywords_config import get_domain_keywords, get_domain_weights


class DomainClassifier:
    """
    Classifies repositories into business/technical domains using weighted keyword matching.
    
    Features:
    - Weighted scoring (AI/ML: 2.0x, Specialized: 1.5x, Generic: 0.8x)
    - Keyword match counting for confidence
    - Primary and secondary domain detection
    """
    
    def __init__(self):
        """Initialize classifier with domain keywords and weights."""
        self.domain_keywords = get_domain_keywords()
        self.domain_weights = get_domain_weights()
        logger.info(f"[TAG]  Domain Classifier initialized with {len(self.domain_keywords)} domains")
    
    def classify_repository(self, repo: Dict) -> Tuple[str, float]:
        """
        Classify a single repository into its primary domain.
        
        Args:
            repo: Repository data with description and topics
            
        Returns:
            Tuple of (primary_domain, confidence_score)
        """
        text = self._prepare_text(repo)
        domain_scores = self._calculate_domain_scores(text)
        
        if not domain_scores:
            return "Software Development", 1.0
        
        primary_domain = max(domain_scores.items(), key=lambda x: x[1])
        return primary_domain
    
    def classify_repositories(self, repos: List[Dict]) -> Dict:
        """
        Classify multiple repositories and aggregate results.
        
        Args:
            repos: List of repository data
            
        Returns:
            Dict with primary_domain, secondary_domains, specializations, evidence
        """
        domain_scores = Counter()
        
        for repo in repos:
            text = self._prepare_text(repo)
            repo_domains = self._calculate_domain_scores(text)
            domain_scores.update(repo_domains)
        
        # Get top domains by weighted score
        top_domains = [d[0] for d in domain_scores.most_common(5)]
        primary_domain = top_domains[0] if top_domains else "Software Development"
        
        return {
            "primary_domain": primary_domain,
            "secondary_domains": top_domains[1:4],
            "specializations": top_domains,
            "evidence": f"Identified projects in {', '.join(top_domains[:3])}"
        }
    
    def _prepare_text(self, repo: Dict) -> str:
        """Prepare searchable text from repository data."""
        description = repo.get('description') or ""
        topics = " ".join(repo.get('topics') or [])
        return (description + " " + topics).lower()
    
    def _calculate_domain_scores(self, text: str) -> Dict[str, float]:
        """
        Calculate weighted scores for all matching domains.
        
        Args:
            text: Lowercase text to search
            
        Returns:
            Dict mapping domain names to weighted scores
        """
        domain_scores = {}
        
        for domain, keywords in self.domain_keywords.items():
            match_count = self._count_keyword_matches(text, keywords)
            
            if match_count > 0:
                weight = self.domain_weights.get(domain, 1.0)
                weighted_score = match_count * weight
                domain_scores[domain] = weighted_score
        
        return domain_scores
    
    def _count_keyword_matches(self, text: str, keywords: List[str]) -> int:
        """
        Count how many keywords match in the text.
        
        Uses word boundary matching for short keywords (<4 chars),
        substring matching for longer keywords.
        """
        match_count = 0
        
        for keyword in keywords:
            if len(keyword) < 4:
                # Short keywords need exact word match
                if re.search(r'\b' + re.escape(keyword) + r'\b', text):
                    match_count += 1
            else:
                # Longer keywords can use substring match
                if keyword in text:
                    match_count += 1
        
        return match_count


# Singleton instance for easy import
domain_classifier = DomainClassifier()
