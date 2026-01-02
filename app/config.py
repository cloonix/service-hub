"""Application configuration using pydantic-settings."""

from pathlib import Path
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # API Settings
    API_TITLE: str = "MyAPI - YouTube Transcript Service"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = (
        "FastAPI backend providing YouTube transcripts and future tools"
    )
    DEBUG: bool = False
    ENVIRONMENT: Literal["development", "staging", "production"] = "development"
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ALLOWED_ORIGINS: list[str] = ["*"]  # Restrict in production

    # Database
    DATABASE_URL: str = "sqlite:///./data/myapi.db"

    # Cache Settings
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 3600  # 1 hour in seconds
    CACHE_MAX_SIZE: int = 100
    CACHE_DIR: Path = Path("./cache")

    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    DEFAULT_RATE_LIMIT: int = 100  # requests
    DEFAULT_RATE_WINDOW: int = 60  # seconds

    # Security
    MASTER_API_KEY: str = ""  # Required - must be set in .env for production
    SECRET_KEY: str = "change-me-in-production"  # For future JWT support

    # YouTube Settings (optional)
    YOUTUBE_COOKIES: str | None = None
    YOUTUBE_PROXY_HTTP: str | None = None
    YOUTUBE_PROXY_HTTPS: str | None = None

    # MCP Server Settings
    MCP_SERVER_HOST: str = "0.0.0.0"
    MCP_SERVER_PORT: int = 8001
    MCP_API_KEY: str | None = None  # Generated during setup
    FASTAPI_URL: str = "http://localhost:8000"

    def ensure_directories(self) -> None:
        """Ensure required directories exist."""
        if self.CACHE_ENABLED and self.CACHE_DIR:
            self.CACHE_DIR.mkdir(parents=True, exist_ok=True)

        # Ensure database directory exists
        db_path = Path(self.DATABASE_URL.replace("sqlite:///", ""))
        db_path.parent.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()

# Ensure directories exist on import
settings.ensure_directories()
