from models import Audit


def assert_audit_modification_access(
    audit: Audit,
    clerk_user_id: str,
    session_token: str | None = None,
) -> None:
    """Verify the caller may purchase, unlock, or link this audit.

    Access is granted when:
    - the audit is already linked to the authenticated user, or
    - the audit is unlinked and the caller presents a valid session token.
    """
    if audit.clerk_user_id == clerk_user_id:
        return

    if audit.clerk_user_id and audit.clerk_user_id != clerk_user_id:
        raise PermissionError("Report access denied.")

    if session_token and audit.session_token == session_token:
        return

    raise PermissionError("Report access denied.")
