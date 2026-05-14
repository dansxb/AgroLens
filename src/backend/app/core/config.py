"""AgroLens application configuration.

Loads all environment variables via Pydantic BaseSettings, providing
type validation, default values, and a single source of truth for
every configuration parameter used across the application.

Usage::

    from app.core.config import settings

    db_url = settings.database_url
"""

from __future__ import annotations

from functools import lru_cache
from typing import List, Optional

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    All fields map 1-to-1 to the environment variables documented in
    ``backend/.env.example``.  Pydantic validates types and raises a
    clear error on startup if a required variable is missing.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ------------------------------------------------------------------
    # Application runtime
    # ------------------------------------------------------------------

    environment: str = Field(
        default="development",
        description="One of: development | staging | production",
    )
    log_level: str = Field(
        default="INFO",
        description="Python logging level.",
    )
    app_version: str = Field(default="0.1.0", description="Semantic version string.")

    # ------------------------------------------------------------------
    # CORS
    # ------------------------------------------------------------------

    allowed_origins: str = Field(
        default="http://localhost:3000",
        description="Comma-separated list of allowed CORS origins.",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse ``ALLOWED_ORIGINS`` into a Python list."""
        return [o.strip() for o in self.allowed_origins.split(",") if o.strip()]

    # ------------------------------------------------------------------
    # Database
    # ------------------------------------------------------------------

    database_url: str = Field(
        ...,
        description=(
            "Async PostgreSQL connection string "
            "(e.g. postgresql+asyncpg://user:pass@host:5432/db)."
        ),
    )
    database_sync_url: str = Field(
        ...,
        description="Synchronous PostgreSQL URL for Alembic.",
    )

    # ------------------------------------------------------------------
    # Security
    # ------------------------------------------------------------------

    secret_key: str = Field(
        ...,
        min_length=32,
        description="FastAPI signing secret; at least 32 random characters.",
    )

    # ------------------------------------------------------------------
    # Supabase
    # ------------------------------------------------------------------

    supabase_url: str = Field(..., description="Supabase project URL.")
    supabase_service_role_key: str = Field(
        ..., description="Supabase service-role key (server-side only)."
    )
    supabase_jwt_secret: str = Field(
        ..., description="JWT secret from Supabase dashboard for token verification."
    )

    # ------------------------------------------------------------------
    # Sentinel Hub
    # ------------------------------------------------------------------

    sentinel_hub_client_id: str = Field(
        ..., description="Sentinel Hub OAuth2 client ID."
    )
    sentinel_hub_client_secret: str = Field(
        ..., description="Sentinel Hub OAuth2 client secret."
    )
    sentinel_hub_instance_id: str = Field(
        ..., description="Sentinel Hub configuration/instance ID."
    )

    # ------------------------------------------------------------------
    # AWS / S3
    # ------------------------------------------------------------------

    aws_access_key_id: str = Field(..., description="AWS IAM access key ID.")
    aws_secret_access_key: str = Field(
        ..., description="AWS IAM secret access key."
    )
    aws_s3_bucket_name: str = Field(
        ..., description="S3 bucket for imagery and export storage."
    )
    aws_s3_region: str = Field(
        default="eu-central-1",
        description="AWS region — must be an EU region for data residency.",
    )

    @field_validator("aws_s3_region")
    @classmethod
    def validate_eu_region(cls, v: str) -> str:
        """Enforce EU data residency requirement."""
        allowed = {"eu-west-1", "eu-west-2", "eu-west-3", "eu-central-1", "eu-north-1"}
        if v not in allowed:
            raise ValueError(
                f"AWS region '{v}' is not an approved EU region. "
                f"Allowed: {', '.join(sorted(allowed))}."
            )
        return v

    # ------------------------------------------------------------------
    # Stripe
    # ------------------------------------------------------------------

    stripe_secret_key: str = Field(..., description="Stripe secret key.")
    stripe_webhook_secret: str = Field(
        ..., description="Stripe webhook signing secret."
    )
    stripe_price_id_starter_monthly: str = Field(
        ..., description="Stripe Price ID — Starter monthly."
    )
    stripe_price_id_starter_annual: str = Field(
        ..., description="Stripe Price ID — Starter annual."
    )
    stripe_price_id_farmer_monthly: str = Field(
        ..., description="Stripe Price ID — Farmer monthly."
    )
    stripe_price_id_farmer_annual: str = Field(
        ..., description="Stripe Price ID — Farmer annual."
    )
    stripe_price_id_pro_monthly: str = Field(
        ..., description="Stripe Price ID — Pro monthly."
    )
    stripe_price_id_pro_annual: str = Field(
        ..., description="Stripe Price ID — Pro annual."
    )

    # ------------------------------------------------------------------
    # SendGrid
    # ------------------------------------------------------------------

    sendgrid_api_key: str = Field(..., description="SendGrid API key.")
    sendgrid_from_email: str = Field(
        ..., description="Verified sender email address."
    )

    # ------------------------------------------------------------------
    # Celery
    # ------------------------------------------------------------------

    celery_broker_url: str = Field(
        ..., description="Redis or RabbitMQ URL for Celery broker."
    )
    celery_result_backend: str = Field(
        ..., description="Celery result backend URL."
    )

    # ------------------------------------------------------------------
    # Sentry
    # ------------------------------------------------------------------

    sentry_dsn: Optional[str] = Field(
        default=None,
        description="Sentry DSN — omit or leave empty to disable error tracking.",
    )

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    monitor_secret_key: str = Field(
        default="change_me_in_production",
        description="Shared secret for the /monitoring/pipeline-health endpoint.",
    )

    # ------------------------------------------------------------------
    # Computed helpers
    # ------------------------------------------------------------------

    @property
    def is_production(self) -> bool:
        """Return True when running in the production environment."""
        return self.environment == "production"

    @property
    def is_development(self) -> bool:
        """Return True when running in development."""
        return self.environment == "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached application settings singleton.

    The ``@lru_cache`` decorator ensures the ``.env`` file is read
    and validated exactly once at startup.

    Returns:
        A validated :class:`Settings` instance.
    """
    return Settings()


#: Module-level settings singleton — import this everywhere.
settings: Settings = get_settings()
