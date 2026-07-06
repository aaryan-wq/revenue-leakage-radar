"""Performance tests for paginated findings queries."""

from __future__ import annotations

import secrets
import time
import uuid
from decimal import Decimal

import pytest

from database.session import SessionLocal
from models import Audit, Finding, Report
from reports.pagination import query_report_findings


def _seed_findings(db, audit_id: uuid.UUID, count: int) -> Report:
    report = Report(
        audit_id=audit_id,
        recoverable_arr=Decimal(str(count * 100)),
        finding_count=count,
        purchased=True,
    )
    db.add(report)
    db.flush()

    findings = [
        Finding(
            audit_id=audit_id,
            rule_id="legacy_pricing",
            rule_name="Legacy Pricing",
            severity="high",
            confidence=Decimal("90"),
            estimated_monthly_loss=Decimal("100"),
            estimated_arr_loss=Decimal(str(1000 + index)),
            attribution="primary",
        )
        for index in range(count)
    ]
    db.add_all(findings)
    db.commit()
    db.refresh(report)
    return report


@pytest.mark.parametrize("finding_count", [500])
def test_paginated_findings_query_under_budget(finding_count: int):
    db = SessionLocal()
    audit = Audit(session_token=secrets.token_urlsafe(32), status="completed")
    db.add(audit)
    db.commit()
    db.refresh(audit)

    try:
        report = _seed_findings(db, audit.id, finding_count)

        start = time.perf_counter()
        page = query_report_findings(db, report, page=1, page_size=25)
        elapsed_ms = (time.perf_counter() - start) * 1000

        assert page["total"] == finding_count
        assert len(page["items"]) == 25
        assert elapsed_ms < 500
    finally:
        db.query(Finding).filter(Finding.audit_id == audit.id).delete(synchronize_session=False)
        db.query(Report).filter(Report.audit_id == audit.id).delete(synchronize_session=False)
        db.delete(audit)
        db.commit()
        db.close()
