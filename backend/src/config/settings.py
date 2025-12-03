"""Application settings using Pydantic Settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "Trade Backend"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/trade"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
