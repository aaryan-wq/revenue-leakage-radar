import os
from pathlib import Path

from pydantic import model_validator
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
    environment: str = "development"
    dev_unlock_enabled: bool = False
    celery_task_always_eager: bool = False
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_price_single_report: str = ""
    stripe_price_annual_membership: str = ""
    annual_membership_report_credits: int = 12
    web_url: str = "http://localhost:3000"
    support_email: str = "contact@paevo.co"
    posthog_api_key: str = ""
    posthog_host: str = "https://us.i.posthog.com"

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
            if public_web_url:
                self.web_url = public_web_url
        return self

    @property
    def clerk_auth_configured(self) -> bool:
        if self.clerk_jwt_issuer and "your-clerk-instance" not in self.clerk_jwt_issuer:
            return True
        return bool(self.clerk_secret_key and "your_key_here" not in self.clerk_secret_key)

    @property
    def stripe_configured(self) -> bool:
        return bool(
            self.stripe_secret_key
            and self.stripe_price_single_report
            and self.stripe_price_annual_membership
        )

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
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


settings = Settings()
