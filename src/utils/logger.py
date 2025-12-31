"""Logging configuration for production"""
import logging
import sys
from pathlib import Path

# Import will be available after config.py is created
try:
    from config import settings
    log_level = settings.LOG_LEVEL
except ImportError:
    log_level = "INFO"


def setup_logger(name: str = "github-analyzer") -> logging.Logger:
    """
    Configure production logging with console output
    
    Args:
        name: Logger name
    
    Returns:
        Configured logger instance
    """
    
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level))
    
    # Formatter with timestamp
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler if not already added
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger


# Create default logger instance
logger = setup_logger()
