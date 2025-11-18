"""Application configuration management."""

from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields from root .env (CrewAI config)
    )

    # API Configuration
    api_host: str = Field(default="0.0.0.0", description="Host to bind the API server")  # nosec B104
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

    # Redis & Celery
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL for Celery",
    )
    celery_broker_url: str = Field(
        default="", description="Celery broker URL (auto-set from redis_url)"
    )
    celery_result_backend: str = Field(
        default="", description="Celery result backend URL (auto-set from redis_url)"
    )

    # File Storage
    stories_data_dir: str = Field(
        default="data/stories",
        description="Base directory for storing generated story files",
    )
    templates_dir: str = Field(
        default="data/templates",
        description="Directory containing template YAML files",
    )
    themes_dir: str = Field(
        default="data/themes",
        description="Directory containing theme configurations",
    )

    @model_validator(mode="after")
    def set_celery_urls(self) -> "Settings":
        """Set Celery URLs from Redis URL if not provided."""
        if not self.celery_broker_url:
            self.celery_broker_url = self.redis_url
        if not self.celery_result_backend:
            self.celery_result_backend = self.redis_url
        return self


settings = Settings()
