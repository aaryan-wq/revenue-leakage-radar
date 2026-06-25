import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from audit.service import get_audit_by_id
from core.config import settings
from database.session import get_db

logger = logging.getLogger(__name__)


async def get_optional_clerk_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None

    if not settings.clerk_secret_key:
        return None

    token = authorization.removeprefix("Bearer ").strip()
    try:
        payload = jwt.decode(
            token,
            settings.clerk_secret_key,
            algorithms=["RS256", "HS256"],
            options={"verify_aud": False},
        )
        user_id = payload.get("sub")
        return str(user_id) if user_id else None
    except JWTError:
        logger.warning("Invalid Clerk JWT token")
        return None


async def require_clerk_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str:
    user_id = await get_optional_clerk_user_id(authorization)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required.",
        )
    return user_id


async def verify_audit_session(
    audit_id: UUID,
    x_audit_session: Annotated[str | None, Header(alias="X-Audit-Session")] = None,
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
):
    audit = get_audit_by_id(db, audit_id)
    if not audit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit not found.",
        )

    if clerk_user_id and audit.clerk_user_id == clerk_user_id:
        return audit

    if x_audit_session and audit.session_token == x_audit_session:
        return audit

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Invalid audit session.",
    )
