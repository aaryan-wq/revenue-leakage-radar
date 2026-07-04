import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import router as audit_router
from auth.clerk_jwt import resolve_clerk_issuer
from core.config import settings
from core.rate_limit import RateLimitMiddleware
from payments.routes import router as payments_router
from reports.routes import router as reports_router
from schemas import HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    upload_path = Path(settings.upload_dir)
    upload_path.mkdir(parents=True, exist_ok=True)
    logger.info("Upload directory ready at %s", upload_path.resolve())
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
    yield
    from analytics.client import shutdown as shutdown_analytics

    shutdown_analytics()


app = FastAPI(
    title="Revenue Leakage Radar API",
    version="0.1.0",
    lifespan=lifespan,
)

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


@app.get("/health", response_model=HealthResponse, tags=["health"])
def health_check() -> HealthResponse:
    return HealthResponse()
