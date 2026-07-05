import re
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

_WINDOW_SECONDS = 60
_ROUTE_LIMITS: list[tuple[re.Pattern[str], int]] = [
    (re.compile(r"^POST /audit$"), 20),
    (re.compile(r"^POST /audit/[^/]+/upload$"), 40),
    (re.compile(r"^POST /webhooks/stripe$"), 120),
    (re.compile(r"^POST /audit/[^/]+/scan$"), 30),
    (re.compile(r"^POST /audit/[^/]+/validate$"), 30),
]
_DEFAULT_LIMIT = 300


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app) -> None:
        super().__init__(app)
        self._hits: dict[str, list[float]] = defaultdict(list)

    def _limit_for(self, method: str, path: str) -> int:
        route_key = f"{method} {path}"
        for pattern, limit in _ROUTE_LIMITS:
            if pattern.match(route_key):
                return limit
        return _DEFAULT_LIMIT

    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        route_key = f"{request.method} {request.url.path}"
        bucket_key = f"{client_ip}:{route_key}"
        limit = self._limit_for(request.method, request.url.path)
        now = time.time()
        window_start = now - _WINDOW_SECONDS
        hits = [timestamp for timestamp in self._hits[bucket_key] if timestamp > window_start]
        if len(hits) >= limit:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please try again shortly."},
            )
        hits.append(now)
        self._hits[bucket_key] = hits
        return await call_next(request)
