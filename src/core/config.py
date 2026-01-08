"""Configuration loader from environment variables"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Optional
from pathlib import Path


# Get .env file path (now in core/, need to go up two directories)
ENV_FILE = Path(__file__).parent.parent.parent / ".env"


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
    
    # LLM Configuration (Optional - for AI Reports)
    # Ollama (Local LLM - Zero Cost)
    USE_OLLAMA: bool = False  # Set to True to use local Ollama instead of cloud APIs
    OLLAMA_URL: str = "http://localhost:11434"  # Ollama server URL
    OLLAMA_MODEL: str = "llama3.1:8b"  # Model to use (llama3.1:8b, llama3.1:70b, etc.)
    
    # Cloud LLM Providers (Fallback when Ollama disabled or fails)
    LLM_PROVIDER: str = "groq"  # groq, openai, or google
    GROQ_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    LLM_MODEL: str = "llama-3.3-70b-versatile"
    LLM_TEMPERATURE: float = 0.1
    LLM_MAX_TOKENS: int = 4096  # Increased for complete reports
    
    model_config = ConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        case_sensitive=True
    )


# Load settings once at startup
settings = Settings()

print(f"[OK] Settings loaded: App ID {settings.GITHUB_APP_ID}, Installation {settings.GITHUB_INSTALLATION_ID}")
