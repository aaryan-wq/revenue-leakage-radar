import logging
import uuid

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.verification.run_verification", bind=True, max_retries=0)
def run_verification_task(self, audit_id: str) -> dict[str, str]:
    from database.session import SessionLocal
    from verification.engine.pipeline import run_verification_pipeline

    db = SessionLocal()
    try:
        run_verification_pipeline(db, uuid.UUID(audit_id))
        from audit.service import get_audit_by_id

        audit = get_audit_by_id(db, uuid.UUID(audit_id))
        return {"status": audit.status if audit else "error", "audit_id": audit_id}
    finally:
        db.close()
