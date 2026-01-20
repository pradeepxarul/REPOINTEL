"""
Enhanced Error Handling Module

Provides robust error handling for production-grade reliability.
Ensures the API never crashes and always returns meaningful responses.
"""

from typing import Dict, Any, Optional, Callable
from functools import wraps
import traceback
from utils.logger import logger


class APIError(Exception):
    """Base exception for API errors."""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict] = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(APIError):
    """Validation error (400)."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, status_code=400, details=details)


class NotFoundError(APIError):
    """Resource not found (404)."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, status_code=404, details=details)


class RateLimitError(APIError):
    """Rate limit exceeded (429)."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, status_code=429, details=details)


class ServiceError(APIError):
    """Internal service error (500)."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, status_code=500, details=details)


def safe_execute(fallback_value: Any = None, log_errors: bool = True):
    """
    Decorator for safe function execution with fallback.
    
    Prevents crashes by catching all exceptions and returning fallback value.
    """
    def decorator(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_errors:
                    logger.error(f"Error in {func.__name__}: {str(e)}")
                    logger.debug(traceback.format_exc())
                return fallback_value
        return wrapper
    return decorator


def validate_input(data: Dict, required_fields: list, field_types: Optional[Dict] = None) -> None:
    """
    Validate input data.
    
    Args:
        data: Input dictionary to validate
        required_fields: List of required field names
        field_types: Optional dict mapping field names to expected types
        
    Raises:
        ValidationError: If validation fails
    """
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(
            f"Missing required fields: {', '.join(missing_fields)}",
            details={'missing_fields': missing_fields}
        )
    
    if field_types:
        type_errors = []
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                type_errors.append({
                    'field': field,
                    'expected': expected_type.__name__,
                    'got': type(data[field]).__name__
                })
        
        if type_errors:
            raise ValidationError(
                "Invalid field types",
                details={'type_errors': type_errors}
            )


def safe_get(data: Dict, *keys, default: Any = None) -> Any:
    """
    Safely get nested dictionary value with default fallback.
    
    Args:
        data: Dictionary to access
        *keys: Sequence of keys for nested access
        default: Default value if key not found
        
    Returns:
        Value if found, default otherwise
    """
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def ensure_type(value: Any, expected_type: type, default: Any = None) -> Any:
    """
    Ensure value is of expected type, return default if not.
    
    Args:
        value: Value to check
        expected_type: Expected type
        default: Default value if type doesn't match
        
    Returns:
        Value if correct type, default otherwise
    """
    if isinstance(value, expected_type):
        return value
    
    # Try type conversion for common cases
    try:
        if expected_type == str:
            return str(value) if value is not None else default
        elif expected_type == int:
            return int(value) if value is not None else default
        elif expected_type == float:
            return float(value) if value is not None else default
        elif expected_type == bool:
            return bool(value) if value is not None else default
        elif expected_type == list:
            return list(value) if value is not None else (default or [])
        elif expected_type == dict:
            return dict(value) if value is not None else (default or {})
    except (ValueError, TypeError):
        pass
    
    return default


class ErrorHandler:
    """Context manager for error handling."""
    
    def __init__(self, operation: str, fallback: Any = None, raise_on_error: bool = False):
        self.operation = operation
        self.fallback = fallback
        self.raise_on_error = raise_on_error
        self.error = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.error = exc_val
            logger.error(f"Error in {self.operation}: {str(exc_val)}")
            logger.debug(traceback.format_exc())
            
            if self.raise_on_error:
                return False  # Re-raise exception
            
            return True  # Suppress exception
        return False
    
    def get_result(self, default_value: Any = None) -> Any:
        """Get result or fallback value if error occurred."""
        return default_value if self.error else self.fallback


# Production-grade error responses
def format_error_response(error: Exception, request_id: str = None) -> Dict[str, Any]:
    """
    Format error as API response.
    
    Args:
        error: Exception that occurred
        request_id: Optional request ID for tracking
        
    Returns:
        Formatted error response dictionary
    """
    if isinstance(error, APIError):
        return {
            'status': 'error',
            'error_code': error.__class__.__name__,
            'error_message': error.message,
            'details': error.details,
            'request_id': request_id
        }
    
    # Generic error
    return {
        'status': 'error',
        'error_code': 'InternalError',
        'error_message': 'An unexpected error occurred',
        'details': {'error_type': type(error).__name__},
        'request_id': request_id
    }
