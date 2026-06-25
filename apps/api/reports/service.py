import uuid
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from models import Report


def upsert_report(
    db: Session,
    audit_id: uuid.UUID,
    recoverable_arr: Decimal,
    finding_count: int,
    confidence: Decimal | None,
) -> Report:
    report = db.query(Report).filter(Report.audit_id == audit_id).first()
    if report:
        report.recoverable_arr = recoverable_arr
        report.finding_count = finding_count
        report.confidence = confidence
        report.generated_at = datetime.now(timezone.utc)
    else:
        report = Report(
            audit_id=audit_id,
            recoverable_arr=recoverable_arr,
            finding_count=finding_count,
            confidence=confidence,
            purchased=False,
            generated_at=datetime.now(timezone.utc),
        )
        db.add(report)
    db.commit()
    db.refresh(report)
    return report
