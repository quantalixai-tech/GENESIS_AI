"""
Genesis API — Centralized Configuration

All configuration is loaded from environment variables via pydantic-settings.
This is the single source of truth for all configuration values.

Usage:
    from core.config import settings
    secret = settings.jwt_secret

Required environment variables (no defaults — will fail on startup if missing):
    JWT_SECRET          — Secret key for signing JWT tokens

Optional environment variables (safe defaults for development):
    DATABASE_URL        — PostgreSQL connection string
    GENESIS_ENV         — Platform environment (development | test | staging | production)
    GENESIS_LOG_LEVEL   — Log verbosity (debug | info | warning | error)
    CORS_ORIGINS        — Comma-separated list of allowed CORS origins
    ACCESS_TOKEN_EXPIRE_MINUTES — JWT token lifetime in minutes
    NATS_URL            — NATS connection URL
    OLLAMA_BASE_URL     — Ollama local LLM endpoint
    PROJECTS_ROOT       — Filesystem root for per-project git repositories
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Platform configuration.

    Values are loaded from environment variables. Pydantic-settings handles
    type coercion, validation, and clear error messages for missing required values.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        # Prevent pydantic-settings from JSON-parsing env strings
        # before our field validators run.
        env_parse_none_str="null",
    )

    # -------------------------------------------------------------------------
    # Platform
    # -------------------------------------------------------------------------
    genesis_env: Literal["development", "test", "staging", "production"] = Field(
        default="development",
        description="Platform environment",
    )
    genesis_log_level: Literal["debug", "info", "warning", "error", "critical"] = Field(
        default="info",
        description="Log verbosity level",
    )

    # -------------------------------------------------------------------------
    # Database
    # -------------------------------------------------------------------------
    database_url: str = Field(
        default="postgresql://genesis:genesis@localhost:5432/genesis",
        description="PostgreSQL connection string",
    )

    # -------------------------------------------------------------------------
    # Security — JWT
    # -------------------------------------------------------------------------
    jwt_secret: str = Field(
        description="Secret key for signing JWT access tokens. REQUIRED. "
        'Generate with: python -c "import secrets; print(secrets.token_hex(32))"',
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="JWT signing algorithm",
    )
    access_token_expire_minutes: int = Field(
        default=60,
        description="JWT access token lifetime in minutes",
        gt=0,
        le=10080,  # max 7 days
    )

    # -------------------------------------------------------------------------
    # CORS
    # Declared as `str` so pydantic-settings treats it as a raw string and
    # does NOT attempt JSON-parsing before we can split it ourselves.
    # Access as `settings.cors_origins` — returns list[str].
    # -------------------------------------------------------------------------
    cors_origins_raw: str = Field(
        default="http://localhost:3000",
        validation_alias="cors_origins",
        description="Allowed CORS origins — comma-separated.",
    )

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS origins as a list, split from the comma-separated env var."""
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    # -------------------------------------------------------------------------
    # Message bus — NATS (per ADR-005)
    # -------------------------------------------------------------------------
    nats_url: str = Field(
        default="nats://nats:4222",
        description="NATS connection URL for agent task dispatch",
    )

    # -------------------------------------------------------------------------
    # Local LLM — Ollama (per ADR-006)
    # -------------------------------------------------------------------------
    ollama_base_url: str = Field(
        default="http://ollama:11434",
        description="Base URL for Ollama local LLM runtime",
    )

    # -------------------------------------------------------------------------
    # Project filesystem — git repos (per ADR-009)
    # -------------------------------------------------------------------------
    projects_root: str = Field(
        default="/projects",
        description="Root directory for per-project git repositories on the shared volume",
    )

    # -------------------------------------------------------------------------
    # API
    # -------------------------------------------------------------------------
    api_version: str = Field(default="v1", description="API version prefix")
    api_title: str = Field(default="Genesis API", description="OpenAPI title")
    api_description: str = Field(
        default="Genesis AI Platform — Core API",
        description="OpenAPI description",
    )

    @property
    def is_production(self) -> bool:
        return self.genesis_env == "production"

    @property
    def is_development(self) -> bool:
        return self.genesis_env == "development"


@lru_cache
def get_settings() -> Settings:
    """
    Return the cached Settings instance.

    Uses lru_cache so the settings object is constructed once per process.
    In tests, call get_settings.cache_clear() before overriding env vars.
    """
    return Settings()


# Module-level convenience alias
settings: Settings = get_settings()
