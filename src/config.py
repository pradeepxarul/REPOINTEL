"""Configuration loader from environment variables"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from pathlib import Path


# Get .env file path (in parent directory of src/)
ENV_FILE = Path(__file__).parent.parent / ".env"


class Settings(BaseSettings):
    """Application settings loaded from .env file"""
    
    # GitHub App Credentials (REQUIRED)
    GITHUB_APP_ID: int
    GITHUB_PRIVATE_KEY: str
    GITHUB_INSTALLATION_ID: int
    
    # Service Configuration
    MAX_REPOS_PER_USER: int = 15
    CACHE_TTL_SECONDS: int = 86400  # 24 hours default
    API_TIMEOUT_SECONDS: int = 10
    LOG_LEVEL: str = "INFO"
    PORT: int = 8000
    ENVIRONMENT: str = "production"
    
    model_config = ConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Load settings once at startup
settings = Settings()

print(f"[OK] Settings loaded: App ID {settings.GITHUB_APP_ID}, Installation {settings.GITHUB_INSTALLATION_ID}")
