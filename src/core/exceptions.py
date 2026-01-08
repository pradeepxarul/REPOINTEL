"""
Custom exception classes for the GitHub User Data Analyzer.

This module defines all custom exceptions used throughout the application
for better error handling and more specific error messages.
"""


class GitHubAnalyzerException(Exception):
    """Base exception for all GitHub Analyzer errors."""
    pass


class GitHubAPIError(GitHubAnalyzerException):
    """Raised when GitHub API returns an error."""
    
    def __init__(self, message: str, status_code: int = None):
        self.status_code = status_code
        super().__init__(message)


class UserNotFoundError(GitHubAnalyzerException):
    """Raised when a GitHub user is not found."""
    
    def __init__(self, username: str):
        self.username = username
        super().__init__(f"GitHub user '{username}' not found")


class RateLimitError(GitHubAnalyzerException):
    """Raised when GitHub API rate limit is exceeded."""
    
    def __init__(self, retry_after: int = None):
        self.retry_after = retry_after
        message = "GitHub API rate limit exceeded"
        if retry_after:
            message += f". Retry after {retry_after} seconds"
        super().__init__(message)


class TokenExpiredError(GitHubAnalyzerException):
    """Raised when GitHub App token has expired."""
    pass


class ValidationError(GitHubAnalyzerException):
    """Raised when input validation fails."""
    
    def __init__(self, field: str, message: str):
        self.field = field
        super().__init__(f"Validation error for '{field}': {message}")


class StorageError(GitHubAnalyzerException):
    """Raised when file storage operations fail."""
    pass


class LLMServiceError(GitHubAnalyzerException):
    """Raised when LLM service encounters an error."""
    
    def __init__(self, message: str, provider: str = None):
        self.provider = provider
        super().__init__(message)


class CacheError(GitHubAnalyzerException):
    """Raised when cache operations fail."""
    pass
