"""
Modules Package

This package contains domain-specific business logic modules.
Modules are isolated, reusable components that can be tested independently.

Sub-packages:
- analyzers: GitHub profile analysis engines
"""

from modules.analyzers import (
    domain_classifier,
    tech_analyzer,
    scoring_engine,
    role_recommender,
    dependency_parser
)

__all__ = [
    'domain_classifier',
    'tech_analyzer',
    'scoring_engine',
    'role_recommender',
    'dependency_parser'
]
