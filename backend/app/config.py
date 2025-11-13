"""Application configuration management."""

from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="Host to bind the API server")
    api_port: int = Field(default=8000, description="Port to bind the API server")
    api_environment: Literal["development", "staging", "production"] = Field(
        default="development", description="Runtime environment"
    )

    # Logging
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="Logging level"
    )

    # CORS
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:5173"],
        description="Allowed CORS origins for frontend integration",
    )

    # Database - placeholder for future use
    database_url: str = Field(
        default="sqlite:///./data/database.db",
        description="Database connection URL (placeholder for future use)",
    )

    # Redis - for Celery message broker
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery",
    )


settings = Settings()
