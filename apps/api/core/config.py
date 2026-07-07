import os
from pathlib import Path

from pydantic import AliasChoices, Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_API_ROOT = Path(__file__).resolve().parent.parent
_REPO_ROOT = _API_ROOT.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(
            str(_REPO_ROOT / ".env"),
            str(_API_ROOT.parent / "web" / ".env.local"),
            str(_API_ROOT / ".env"),
        ),
        env_file_encoding="utf-8",
        extra="ignore",
        populate_by_name=True,
    )

    database_url: str = "postgresql://rlr:rlr_dev_password@localhost:5432/revenue_leakage_radar"
    redis_url: str = "redis://localhost:6379/0"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    upload_dir: str = "./uploads"
    max_upload_size_mb: int = 250
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"
    clerk_secret_key: str = ""
    clerk_jwt_issuer: str = ""
    clerk_jwt_audience: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    environment: str = Field(
        default="development",
        validation_alias=AliasChoices("ENVIRONMENT", "APP_ENV"),
    )
    dev_unlock_enabled: bool = False
    celery_task_always_eager: bool = False
    celery_worker_concurrency: int = Field(default=2, validation_alias="CELERY_WORKER_CONCURRENCY")
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_single_report: str = Field(
        default="",
        validation_alias=AliasChoices("STRIPE_PRICE_SINGLE_REPORT", "STRIPE_PAID_AUDIT_PRICE_ID"),
    )
    stripe_price_annual_membership: str = ""
    annual_membership_report_credits: int = 12
    web_url: str = Field(
        default="http://localhost:3000",
        validation_alias=AliasChoices("WEB_URL", "FRONTEND_URL", "APP_BASE_URL"),
    )
    support_email: str = "aaryan@paevo.co"
    feedback_email: str = Field(default="aaryan@paevo.co", validation_alias="FEEDBACK_EMAIL")
    from_email: str = Field(default="hello@paevo.co", validation_alias="FROM_EMAIL")
    posthog_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"
    sentry_dsn: str = Field(default="", validation_alias="SENTRY_DSN")
    resend_api_key: str = Field(default="", validation_alias="RESEND_API_KEY")
    storage_backend: str = Field(default="local", validation_alias="STORAGE_BACKEND")
    r2_account_id: str = Field(default="", validation_alias="R2_ACCOUNT_ID")
    r2_access_key_id: str = Field(default="", validation_alias="R2_ACCESS_KEY_ID")
    r2_secret_access_key: str = Field(default="", validation_alias="R2_SECRET_ACCESS_KEY")
    r2_endpoint: str = Field(default="", validation_alias="R2_ENDPOINT")
    r2_bucket_uploads: str = Field(default="paevo-prod-uploads", validation_alias="R2_BUCKET_UPLOADS")
    r2_bucket_reports: str = Field(default="paevo-prod-reports", validation_alias="R2_BUCKET_REPORTS")
    allowed_hosts: str = Field(default="*", validation_alias="ALLOWED_HOSTS")

    @model_validator(mode="after")
    def warn_invalid_posthog_key(self) -> "Settings":
        if self.posthog_api_key.startswith("phx_"):
            import logging

            logging.getLogger(__name__).warning(
                "POSTHOG_API_KEY looks like a personal API key (phx_). "
                "Event capture requires the project API key (phc_) from PostHog → Project Settings."
            )
        return self

    @model_validator(mode="after")
    def resolve_web_url(self) -> "Settings":
        if self.web_url == "http://localhost:3000":
            public_web_url = os.environ.get("NEXT_PUBLIC_WEB_URL", "").strip()
            if not public_web_url:
                public_web_url = os.environ.get("NEXT_PUBLIC_APP_URL", "").strip()
            if public_web_url:
                self.web_url = public_web_url
        return self

    @model_validator(mode="after")
    def resolve_r2_endpoint(self) -> "Settings":
        if self.storage_backend == "r2" and not self.r2_endpoint and self.r2_account_id:
            self.r2_endpoint = f"https://{self.r2_account_id}.r2.cloudflarestorage.com"
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def clerk_auth_configured(self) -> bool:
        if self.clerk_jwt_issuer and "your-clerk-instance" not in self.clerk_jwt_issuer:
            return True
        return bool(self.clerk_secret_key and "your_key_here" not in self.clerk_secret_key)

    @property
    def stripe_configured(self) -> bool:
        return bool(self.stripe_secret_key and self.stripe_price_single_report)

    @property
    def annual_membership_configured(self) -> bool:
        return bool(self.stripe_price_annual_membership)

    @property
    def clerk_jwt_audience_value(self) -> str | None:
        if self.clerk_jwt_audience:
            return self.clerk_jwt_audience
        if self.web_url:
            return self.web_url
        return None

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def allowed_host_list(self) -> list[str]:
        hosts = [host.strip() for host in self.allowed_hosts.split(",") if host.strip()]
        if not hosts:
            return ["*"]
        if self.is_production and "*" not in hosts:
            for host in _RAILWAY_HEALTH_HOSTS:
                if host not in hosts:
                    hosts.append(host)
        return hosts

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


_RAILWAY_HEALTH_HOSTS = ("*.up.railway.app", "*.railway.app", "localhost", "127.0.0.1")

settings = Settings()
