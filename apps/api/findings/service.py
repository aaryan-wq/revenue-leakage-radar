import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from models import Finding
from verification.outputs import rule_finding_to_orm
from verification.types import RuleFinding


def clear_findings(db: Session, audit_id: uuid.UUID) -> None:
    db.query(Finding).filter(Finding.audit_id == audit_id).delete(synchronize_session=False)
    db.commit()


def persist_findings(
    db: Session, audit_id: uuid.UUID, findings: list[RuleFinding]
) -> list[Finding]:
    orm_rows = [rule_finding_to_orm(audit_id, f) for f in findings]
    for row in orm_rows:
        db.add(row)
    db.commit()
    for row in orm_rows:
        db.refresh(row)
    return orm_rows
