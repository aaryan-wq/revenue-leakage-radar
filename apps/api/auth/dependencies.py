import logging
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from audit.service import get_audit_by_id
from auth.clerk_jwt import decode_clerk_token
from core.config import settings
from database.session import get_db

logger = logging.getLogger(__name__)


def _audit_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Audit not found.",
    )


async def get_optional_clerk_user_id(
    authorization: Annotated[str | None, Header()] = None,
) -> str | None:
    if not authorization or not authorization.startswith("Bearer "):
        return None

    if not settings.clerk_auth_configured:
        logger.warning("Clerk auth is not configured on the API, set CLERK_SECRET_KEY or CLERK_JWT_ISSUER.")
        return None

    token = authorization.removeprefix("Bearer ").strip()
    payload = decode_clerk_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token.",
        )

    user_id = payload.get("sub")
    return str(user_id) if user_id else None


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


def _grant_audit_access(
    audit,
    *,
    clerk_user_id: str | None,
    x_audit_session: str | None,
) -> bool:
    if audit.clerk_user_id:
        return bool(clerk_user_id and audit.clerk_user_id == clerk_user_id)

    if x_audit_session and audit.session_token == x_audit_session:
        return True

    return False


async def verify_audit_session(
    audit_id: UUID,
    x_audit_session: Annotated[str | None, Header(alias="X-Audit-Session")] = None,
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
):
    audit = get_audit_by_id(db, audit_id)
    if not audit:
        raise _audit_not_found()

    if not _grant_audit_access(audit, clerk_user_id=clerk_user_id, x_audit_session=x_audit_session):
        raise _audit_not_found()

    return audit


async def verify_audit_write_session(
    audit_id: UUID,
    x_audit_session: Annotated[str | None, Header(alias="X-Audit-Session")] = None,
    db: Session = Depends(get_db),
    clerk_user_id: str | None = Depends(get_optional_clerk_user_id),
):
    """Write access: linked audits require the owning Clerk user; unlinked audits accept session token."""
    return await verify_audit_session(audit_id, x_audit_session, db, clerk_user_id)
