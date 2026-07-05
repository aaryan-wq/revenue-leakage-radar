"""Production startup validation — fail fast when required config is missing."""

from core.config import settings


class StartupConfigurationError(RuntimeError):
    pass


def _require(value: str | None, name: str) -> None:
    if not value or not str(value).strip():
        raise StartupConfigurationError(f"Missing required production environment variable: {name}")


def validate_production_settings() -> None:
    if not settings.is_production:
        return

    _require(settings.database_url, "DATABASE_URL")
    _require(settings.redis_url, "REDIS_URL")
    _require(settings.web_url, "WEB_URL (or FRONTEND_URL / APP_BASE_URL)")
    _require(settings.cors_origins, "CORS_ORIGINS")
    _require(settings.clerk_secret_key, "CLERK_SECRET_KEY")

    if not settings.clerk_jwt_issuer and "your_key_here" in settings.clerk_secret_key:
        raise StartupConfigurationError("CLERK_SECRET_KEY must be a production key")

    _require(settings.stripe_secret_key, "STRIPE_SECRET_KEY")
    _require(settings.stripe_webhook_secret, "STRIPE_WEBHOOK_SECRET")
    _require(settings.stripe_price_single_report, "STRIPE_PRICE_SINGLE_REPORT")
    _require(settings.posthog_api_key, "POSTHOG_API_KEY")
    _require(settings.sentry_dsn, "SENTRY_DSN")
    _require(settings.resend_api_key, "RESEND_API_KEY")
    _require(settings.from_email, "FROM_EMAIL")

    if settings.dev_unlock_enabled:
        raise StartupConfigurationError("DEV_UNLOCK_ENABLED must be false in production")

    if settings.celery_task_always_eager:
        raise StartupConfigurationError("CELERY_TASK_ALWAYS_EAGER must be false in production")

    if settings.storage_backend == "r2":
        _require(settings.r2_account_id, "R2_ACCOUNT_ID")
        _require(settings.r2_access_key_id, "R2_ACCESS_KEY_ID")
        _require(settings.r2_secret_access_key, "R2_SECRET_ACCESS_KEY")
        _require(settings.r2_endpoint, "R2_ENDPOINT")
        _require(settings.r2_bucket_uploads, "R2_BUCKET_UPLOADS")
        _require(settings.r2_bucket_reports, "R2_BUCKET_REPORTS")
