import logging
from contextlib import asynccontextmanager

import redis
import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.starlette import StarletteIntegration
from sqlalchemy import text

from app.routes import router as audit_router
from auth.clerk_jwt import resolve_clerk_issuer
from core.config import settings
from core.rate_limit import RateLimitMiddleware
from core.startup_checks import StartupConfigurationError, validate_production_settings
from database.session import SessionLocal
from feedback.routes import router as feedback_router
from payments.routes import router as payments_router
from reports.routes import router as reports_router
from schemas import HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

if settings.sentry_dsn:
    sentry_sdk.init(
        dsn=settings.sentry_dsn,
        environment=settings.environment,
        integrations=[
            StarletteIntegration(transaction_style="endpoint"),
            FastApiIntegration(transaction_style="endpoint"),
        ],
        traces_sample_rate=0.1 if settings.is_production else 0.0,
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        validate_production_settings()
    except StartupConfigurationError as exc:
        logger.error("Startup configuration error: %s", exc)
        if settings.is_production:
            raise

    if settings.storage_backend == "local":
        from pathlib import Path

        upload_path = Path(settings.upload_dir)
        upload_path.mkdir(parents=True, exist_ok=True)
        logger.info("Upload directory ready at %s", upload_path.resolve())
    else:
        logger.info("Using R2 storage backend (uploads=%s)", settings.r2_bucket_uploads)

    if settings.clerk_auth_configured:
        issuer = resolve_clerk_issuer()
        if issuer:
            logger.info("Clerk JWT verification enabled (issuer: %s)", issuer)
        else:
            logger.warning(
                "Clerk keys are present but JWT issuer could not be resolved. "
                "Set CLERK_JWT_ISSUER in .env to your Clerk Frontend API URL."
            )
    else:
        logger.warning(
            "Clerk auth is not configured on the API. "
            "Copy CLERK_SECRET_KEY from apps/web/.env.local into the root .env, or run clerk init."
        )

    if settings.sentry_dsn:
        logger.info("Sentry error tracking enabled (environment=%s)", settings.environment)
    elif settings.is_production:
        logger.warning("Sentry DSN not configured for production")

    if settings.posthog_api_key:
        logger.info("PostHog product analytics enabled")
    elif settings.is_production:
        logger.warning("PostHog API key not configured for production")

    yield
    from analytics.client import shutdown as shutdown_analytics

    shutdown_analytics()


app = FastAPI(
    title="Revenue Leakage Radar API",
    version="0.1.0",
    lifespan=lifespan,
)

if settings.is_production and settings.allowed_host_list != ["*"]:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_host_list)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RateLimitMiddleware)

app.include_router(audit_router)
app.include_router(reports_router)
app.include_router(payments_router)
app.include_router(feedback_router)


def _check_database() -> bool:
    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:
        logger.exception("Database health check failed")
        return False
    finally:
        db.close()


def _check_redis() -> bool:
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        return bool(client.ping())
    except Exception:
        logger.exception("Redis health check failed")
        return False


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    db_ok = _check_database()
    redis_ok = _check_redis()
    if settings.is_production and (not db_ok or not redis_ok):
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail={
                "status": "degraded",
                "database": db_ok,
                "redis": redis_ok,
            },
        )
    return HealthResponse(
        status="ok" if db_ok and redis_ok else "degraded",
        database=db_ok,
        redis=redis_ok,
    )
