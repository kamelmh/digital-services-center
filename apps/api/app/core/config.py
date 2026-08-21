"""Core config — pydantic-settings, no hardcoded secrets."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    # App
    app_name: str = "DSC Digital Services Center API"
    app_env: Literal["development", "production", "test"] = Field(default="development", alias="APP_ENV")
    api_v1_prefix: str = "/v1"

    # DB — SQLite for local dev (separate from Violit's dsc_data.db), Postgres for SaaS
    database_url: str = Field(default="sqlite:///./apps/api/dsc_saas.db", alias="DATABASE_URL")

    # Redis / RQ
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    rq_queue_name: str = "dsc-queue"

    # Auth
    jwt_secret: str = Field(default="change-me-in-prod-32-bytes-min", alias="DSC_JWT_SECRET")
    jwt_alg: str = "HS256"
    jwt_expire_hours: int = 72
    auth_required: bool = Field(default=False, alias="DSC_AUTH_REQUIRED")  # SaaS: True

    # LLM providers
    groq_api_key: str | None = Field(default=None, alias="GROQ_API_KEY")
    openrouter_api_key: str | None = Field(default=None, alias="OPENROUTER_API_KEY")
    aihubmix_api_key: str | None = Field(default=None, alias="AIHUBMIX_API_KEY")

    # Storage — local fallback, R2 for SaaS
    storage_backend: Literal["local", "r2"] = Field(default="local", alias="STORAGE_BACKEND")
    r2_endpoint: str | None = Field(default=None, alias="R2_ENDPOINT")
    r2_access_key: str | None = Field(default=None, alias="R2_ACCESS_KEY")
    r2_secret_key: str | None = Field(default=None, alias="R2_SECRET_KEY")
    r2_bucket: str | None = Field(default=None, alias="R2_BUCKET")
    r2_presign_seconds: int = 900  # 15m

    # Billing
    billing_gateway: Literal["mock", "chargily", "stripe"] = Field(default="mock", alias="DSC_BILLING_GATEWAY")
    chargily_key: str | None = Field(default=None, alias="DSC_CHARGILY_KEY")
    chargily_secret: str | None = Field(default=None, alias="DSC_CHARGILY_SECRET")
    billing_webhook_secret: str | None = Field(default=None, alias="DSC_BILLING_WEBHOOK_SECRET")
    frontend_url: str = Field(default="http://localhost:3000", alias="DSC_FRONTEND_URL")
    webhook_url: str | None = Field(default=None, alias="DSC_WEBHOOK_URL")

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

# Hardened check: fail fast if default JWT secret is used in production
if settings.app_env == "production" and settings.jwt_secret == "change-me-in-prod-32-bytes-min":
    raise ValueError("DSC_JWT_SECRET must be set to a strong random value in production (APP_ENV=production). Generate with: python -c \"import secrets; print(secrets.token_hex(32))\"")
if settings.app_env == "production" and settings.auth_required is False:
    import warnings

    warnings.warn("APP_ENV=production but DSC_AUTH_REQUIRED is not set — enabling auth is recommended for SaaS")
