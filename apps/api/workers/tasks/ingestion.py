import logging
import uuid

from audit.service import get_audit_by_id
from database.session import SessionLocal
from ingestion.pipeline import run_ingestion_pipeline
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="workers.tasks.ingestion.run_ingestion", bind=True, max_retries=0)
def run_ingestion_task(self, audit_id: str) -> dict[str, str]:

    db = SessionLocal()
    try:
        audit = get_audit_by_id(db, uuid.UUID(audit_id))
        if not audit:
            logger.error("Audit not found: %s", audit_id)
            return {"status": "error", "message": "Audit not found"}

        run_ingestion_pipeline(db, audit)
        db.refresh(audit)
        return {"status": audit.status, "audit_id": audit_id}
    finally:
        db.close()
