"""
Analyzers Module

Domain-specific analysis engines for GitHub profile analysis.
Each analyzer is responsible for a specific aspect of the analysis.

Analyzers:
- domain_classifier: Classify repositories into business domains
- tech_analyzer: Analyze technology stack and frameworks
- scoring_engine: Calculate metrics and scores
- role_recommender: Recommend suitable roles
- dependency_parser: Parse dependency manifest files
"""

from modules.analyzers.domain_classifier import domain_classifier
from modules.analyzers.tech_analyzer import tech_analyzer
from modules.analyzers.scoring_engine import scoring_engine
from modules.analyzers.role_recommender import role_recommender
from modules.analyzers.dependency_parser import dependency_parser
from modules.analyzers.readme_analyzer import readme_analyzer

__all__ = [
    'domain_classifier',
    'tech_analyzer',
    'scoring_engine',
    'role_recommender',
    'dependency_parser',
    'readme_analyzer'
]
