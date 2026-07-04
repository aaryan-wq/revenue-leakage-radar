import logging
import time
from typing import Any

import httpx
from jose import JWTError, jwk, jwt

from core.config import settings

logger = logging.getLogger(__name__)

_JWKS_CACHE: dict[str, tuple[float, dict[str, Any]]] = {}
_JWKS_TTL_SECONDS = 3600
_RESOLVED_ISSUER: str | None = None


def _is_placeholder(value: str) -> bool:
    return not value or "your_key_here" in value or "your-clerk-instance" in value


def resolve_clerk_issuer() -> str | None:
    global _RESOLVED_ISSUER

    if _RESOLVED_ISSUER:
        return _RESOLVED_ISSUER

    if settings.clerk_jwt_issuer and not _is_placeholder(settings.clerk_jwt_issuer):
        _RESOLVED_ISSUER = settings.clerk_jwt_issuer.rstrip("/")
        return _RESOLVED_ISSUER

    if _is_placeholder(settings.clerk_secret_key):
        return None

    try:
        response = httpx.get(
            "https://api.clerk.com/v1/instance",
            headers={"Authorization": f"Bearer {settings.clerk_secret_key}"},
            timeout=10.0,
        )
        response.raise_for_status()
        data = response.json()
        frontend_api = data.get("frontend_api_url") or data.get("frontend_api")
        if isinstance(frontend_api, str) and frontend_api:
            issuer = frontend_api if frontend_api.startswith("https://") else f"https://{frontend_api}"
            _RESOLVED_ISSUER = issuer.rstrip("/")
            logger.info("Resolved Clerk JWT issuer from instance API.")
            return _RESOLVED_ISSUER
    except httpx.HTTPError as exc:
        logger.warning("Failed to resolve Clerk issuer from instance API: %s", exc)

    return None


def _get_jwks(issuer: str) -> dict[str, Any]:
    now = time.time()
    cached = _JWKS_CACHE.get(issuer)
    if cached and now - cached[0] < _JWKS_TTL_SECONDS:
        return cached[1]

    jwks_url = f"{issuer}/.well-known/jwks.json"
    response = httpx.get(jwks_url, timeout=10.0)
    response.raise_for_status()
    jwks = response.json()
    _JWKS_CACHE[issuer] = (now, jwks)
    return jwks


def _find_rsa_key(jwks: dict[str, Any], kid: str) -> dict[str, Any] | None:
    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key
    return None


def decode_clerk_token(token: str) -> dict[str, Any] | None:
    issuer = resolve_clerk_issuer()
    if not issuer:
        logger.warning("Clerk JWT issuer is not configured.")
        return None

    try:
        header = jwt.get_unverified_header(token)
        kid = header.get("kid")
        if not kid:
            raise JWTError("Token header missing kid.")

        jwks = _get_jwks(issuer)
        rsa_key = _find_rsa_key(jwks, kid)
        if not rsa_key:
            _JWKS_CACHE.pop(issuer, None)
            jwks = _get_jwks(issuer)
            rsa_key = _find_rsa_key(jwks, kid)
        if not rsa_key:
            raise JWTError("Matching JWK not found.")

        public_key = jwk.construct(rsa_key)
        decode_options: dict[str, bool] = {"verify_aud": False}
        audience = settings.clerk_jwt_audience_value
        if audience:
            decode_options["verify_aud"] = True
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=issuer,
            audience=audience,
            options=decode_options,
        )
        return payload
    except JWTError as exc:
        logger.warning("Clerk JWT verification failed: %s", exc)
        return None
    except httpx.HTTPError as exc:
        logger.warning("Failed to fetch Clerk JWKS: %s", exc)
        return None
