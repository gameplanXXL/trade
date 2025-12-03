"""Application settings using Pydantic Settings."""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application configuration settings.

    All settings can be configured via environment variables.
    Required settings without defaults will prevent app start if missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ==========================================================================
    # Application
    # ==========================================================================
    app_name: str = "Trade Backend"
    environment: Literal["development", "staging", "production"] = "development"
    debug: bool = False

    # ==========================================================================
    # Server
    # ==========================================================================
    api_host: str = Field(default="0.0.0.0", description="API server host")
    api_port: int = Field(default=8000, ge=1, le=65535, description="API server port")

    # ==========================================================================
    # Database
    # ==========================================================================
    database_url: str = Field(
        ...,  # Required
        description="PostgreSQL connection URL (postgresql+asyncpg://user:pass@host:port/db)",
    )

    # ==========================================================================
    # Redis
    # ==========================================================================
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        description="Redis connection URL",
    )

    # ==========================================================================
    # Security
    # ==========================================================================
    secret_key: str = Field(
        ...,  # Required
        min_length=32,
        description="Secret key for session signing (min 32 chars)",
    )
    encryption_key: str = Field(
        default="",
        description="Fernet encryption key for credentials",
    )

    # ==========================================================================
    # LLM Configuration
    # ==========================================================================
    anthropic_api_key: str | None = Field(
        default=None,
        description="Anthropic API key for Claude models",
    )
    openai_api_key: str | None = Field(
        default=None,
        description="OpenAI API key (optional)",
    )

    # ==========================================================================
    # MT5 Configuration
    # ==========================================================================
    mt5_login: int | None = Field(
        default=None,
        description="MetaTrader 5 account login",
    )
    mt5_password: str | None = Field(
        default=None,
        description="MetaTrader 5 account password",
    )
    mt5_server: str | None = Field(
        default=None,
        description="MetaTrader 5 server address",
    )

    # ==========================================================================
    # Logging
    # ==========================================================================
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"
    log_format: Literal["json", "console"] = "json"

    # ==========================================================================
    # Performance
    # ==========================================================================
    pipeline_timeout_seconds: int = Field(
        default=1,
        ge=1,
        le=60,
        description="Maximum time for pipeline execution",
    )
    db_pool_size: int = Field(
        default=5,
        ge=1,
        le=50,
        description="Database connection pool size",
    )
    db_max_overflow: int = Field(
        default=10,
        ge=0,
        le=100,
        description="Database connection pool max overflow",
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """Ensure secret key is sufficiently secure."""
        if len(v) < 32:
            raise ValueError("secret_key must be at least 32 characters")
        return v

    @field_validator("encryption_key")
    @classmethod
    def validate_encryption_key(cls, v: str) -> str:
        """Validate Fernet key format if provided."""
        if v and len(v) != 44:
            raise ValueError(
                "encryption_key must be a valid Fernet key (44 characters)"
            )
        return v

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment == "development"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Uses LRU cache to ensure settings are only loaded once.
    Call get_settings.cache_clear() to reload settings.

    Raises:
        ValidationError: If required environment variables are missing or invalid.
    """
    return Settings()
