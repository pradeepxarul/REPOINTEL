"""
Statistical keyword extraction using YAKE algorithm.
Extracts compound technical terms ("machine learning", "web development")
100% deterministic - no AI/ML models.
"""

from typing import List
from dataclasses import dataclass
try:
    import yake
    YAKE_AVAILABLE = True
except ImportError:
    YAKE_AVAILABLE = False
from utils.logger import logger


@dataclass
class ScoredKeyword:
    keyword: str
    score: float  # Lower = better
    source: str = "statistical"


class StatisticalKeywordExtractor:
    """Extracts keywords using YAKE statistical analysis."""
    
    def __init__(self, language="en", max_ngram_size=3, num_keywords=30):
        self.available = YAKE_AVAILABLE
        self.language = language
        self.max_ngram_size = max_ngram_size
        self.num_keywords = num_keywords
        
        # Technical term indicators
        self.technical_terms = {
            'programming', 'framework', 'library', 'api', 'sdk', 'database',
            'server', 'development', 'software', 'web', 'mobile', 'cloud'
        }
        
        if not self.available:
            logger.warning("[STATISTICAL] YAKE not available")
    
    def extract(self, text: str, max_keywords: int = None) -> List[ScoredKeyword]:
        """Extract top keywords from text."""
        if not text or not text.strip():
            return []
        
        num_kw = max_keywords if max_keywords else self.num_keywords
        
        if self.available:
            return self._extract_yake(text, num_kw)
        else:
            return self._extract_simple(text, num_kw)
    
    def _extract_yake(self, text: str, num_keywords: int) -> List[ScoredKeyword]:
        """Extract using YAKE library."""
        try:
            extractor = yake.KeywordExtractor(
                lan=self.language,
                n=self.max_ngram_size,
                dedupLim=0.9,
                top=num_keywords
            )
            
            keywords = extractor.extract_keywords(text)
            
            scored = [
                ScoredKeyword(keyword=kw, score=score, source="yake")
                for kw, score in keywords
            ]
            
            logger.info(f"[YAKE] Extracted {len(scored)} keywords")
            return scored
            
        except Exception as e:
            logger.error(f"[YAKE] Failed: {e}")
            return self._extract_simple(text, num_keywords)
    
    def _extract_simple(self, text: str, num_keywords: int) -> List[ScoredKeyword]:
        """Fallback - basic frequency analysis."""
        import re
        from collections import Counter
        
        # Extract words (3+ chars)
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        word_freq = Counter(words)
        top_words = word_freq.most_common(num_keywords)
        
        # Convert to scored keywords
        max_freq = max(freq for _, freq in top_words) if top_words else 1
        scored = [
            ScoredKeyword(
                keyword=word,
                score=1.0 - (freq / max_freq),
                source="frequency"
            )
            for word, freq in top_words
        ]
        
        logger.info(f"[FALLBACK] Extracted {len(scored)} keywords")
        return scored
    
    def filter_technical(
        self,
        keywords: List[ScoredKeyword],
        threshold: float = 0.5
    ) -> List[ScoredKeyword]:
        """Keep only technical-looking keywords."""
        technical = []
        
        for kw in keywords:
            # YAKE: lower score = better
            if kw.score <= threshold:
                kw_lower = kw.keyword.lower()
                
                # Check if technical
                is_technical = any(term in kw_lower for term in self.technical_terms)
                is_compound = ' ' in kw.keyword  # Multi-word phrases
                has_capitals = any(c.isupper() for c in kw.keyword)  # Framework names
                
                if is_technical or is_compound or has_capitals:
                    technical.append(kw)
        
        return technical
    
    def merge_with_patterns(
        self,
        statistical_kws: List[ScoredKeyword],
        pattern_kws: List[str],
        prefer_statistical: bool = False
    ) -> List[str]:
        """Merge statistical and pattern-based keywords."""
        stat_set = {kw.keyword.lower() for kw in statistical_kws}
        pattern_set = {kw.lower() for kw in pattern_kws}
        
        if prefer_statistical:
            # Start with statistical
            merged = list(stat_set)
            merged.extend(kw for kw in pattern_set if kw not in stat_set)
        else:
            # Start with patterns (more precise)
            merged = list(pattern_set)
            merged.extend(kw for kw in stat_set if kw not in pattern_set)
        
        logger.info(f"[MERGE] {len(stat_set)} + {len(pattern_set)} = {len(merged)} keywords")
        return merged


# Global instance
statistical_keyword_extractor = StatisticalKeywordExtractor(
    language="en",
    max_ngram_size=3,  # "machine learning", "web development"
    num_keywords=30
)
