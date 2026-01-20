"""
Controllers Package

This package contains HTTP request handlers following MVC architecture.
Controllers are responsible for:
- Handling HTTP requests and responses
- Input validation (delegated to Pydantic)
- Calling appropriate services
- Formatting responses

No business logic should be in controllers - delegate to services.
"""

from controllers.analysis_controller import AnalysisController
from controllers.report_controller import ReportController

__all__ = [
    'AnalysisController',
    'ReportController'
]
