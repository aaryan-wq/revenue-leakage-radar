import logging
import uuid

from database.session import SessionLocal
from verification.engine.pipeline import run_verification_pipeline
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.verification.run_verification", bind=True, max_retries=0)
def run_verification_task(self, audit_id: str) -> dict[str, str]:

    db = SessionLocal()
    try:
        run_verification_pipeline(db, uuid.UUID(audit_id))
        from audit.service import get_audit_by_id
        from core.config import settings
        from core.enums import AuditStatus
        from notifications.clerk import fetch_clerk_user_email
        from notifications.templates import report_ready_email

        audit = get_audit_by_id(db, uuid.UUID(audit_id))
        if audit and audit.status == AuditStatus.COMPLETED.value and audit.clerk_user_id:
            email = fetch_clerk_user_email(audit.clerk_user_id)
            if email:
                summary_url = f"{settings.web_url}/summary/{audit.id}"
                report_ready_email(to=email, summary_url=summary_url)
        return {"status": audit.status if audit else "error", "audit_id": audit_id}
    except Exception:
        logger.exception("Verification task failed for audit %s", audit_id)
        try:
            import sentry_sdk

            sentry_sdk.capture_exception()
        except Exception:
            pass
        raise
    finally:
        db.close()
