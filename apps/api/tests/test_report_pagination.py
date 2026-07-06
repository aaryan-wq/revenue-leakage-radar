"""Tests for paginated report findings API."""

from __future__ import annotations

import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from models import Audit, Finding, Report
from reports.generator import build_report_detail
from reports.pagination import build_primary_lookup_for_finding, query_report_findings


def _finding(
    audit_id: uuid.UUID,
    *,
    rule_id: str = "legacy_pricing",
    arr: str = "1000",
    finding_ref: str | None = None,
    primary_finding_ref: str | None = None,
) -> Finding:
    return Finding(
        id=uuid.uuid4(),
        audit_id=audit_id,
        rule_id=rule_id,
        rule_name=rule_id.replace("_", " ").title(),
        severity="high",
        confidence=Decimal("90"),
        estimated_monthly_loss=Decimal(arr) / Decimal("12"),
        estimated_arr_loss=Decimal(arr),
        finding_ref=finding_ref,
        primary_finding_ref=primary_finding_ref,
        attribution="primary" if not primary_finding_ref else "secondary",
    )


def test_build_report_detail_omits_findings_by_default():
    db = MagicMock()
    audit = Audit(session_token="token")
    audit.id = uuid.uuid4()
    audit.company = None
    audit.scan_report = {"rules_completed": 1, "rules_total": 1}
    report = Report(audit_id=audit.id, recoverable_arr=Decimal("1000"), finding_count=2)

    findings = [
        _finding(audit.id, arr="2000"),
        _finding(audit.id, arr="1000"),
    ]

    db.query.return_value.filter.return_value.first.side_effect = [audit]
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = findings

    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr(
            "reports.generator.build_free_summary",
            lambda _db, _audit, findings=None: {
                "recoverable_arr": "1000",
                "confidence": "90",
                "finding_count": 2,
                "accounts_reviewed": 1,
                "invoices_reviewed": 1,
                "rules_completed": 1,
                "rules_total": 1,
                "opportunity_breakdown": [],
                "verification_checks": [],
                "locked_preview": [],
                "reconciliation": None,
            },
        )
        patcher.setattr(
            "reports.generator.generate_executive_narrative",
            lambda _summary: "Summary narrative.",
        )
        detail = build_report_detail(db, report, include_findings=False)

    assert detail["findings_total"] == 2
    assert detail["findings"] == []


def test_query_report_findings_paginates():
    db = MagicMock()
    audit_id = uuid.uuid4()
    report = Report(audit_id=audit_id, recoverable_arr=Decimal("0"), finding_count=3)
    findings = [
        _finding(audit_id, arr="3000"),
        _finding(audit_id, arr="2000"),
        _finding(audit_id, arr="1000"),
    ]

    base_query = db.query.return_value.filter.return_value
    base_query.count.return_value = 3
    base_query.order_by.return_value.offset.return_value.limit.return_value.all.return_value = findings[:2]

    with pytest.MonkeyPatch.context() as patcher:
        patcher.setattr(
            "reports.pagination.EntityIdResolver.for_findings",
            lambda _db, _findings: MagicMock(),
        )
        patcher.setattr(
            "reports.pagination.serialize_finding",
            lambda finding, **kwargs: {"id": str(finding.id), "rule_id": finding.rule_id},
        )
        data = query_report_findings(db, report, page=1, page_size=2)

    assert data["total"] == 3
    assert data["page"] == 1
    assert data["page_size"] == 2
    assert data["has_more"] is True
    assert len(data["items"]) == 2


def test_build_primary_lookup_for_finding_loads_single_reference():
    db = MagicMock()
    audit_id = uuid.uuid4()
    primary = _finding(audit_id, finding_ref="primary_ref", arr="500")
    secondary = _finding(
        audit_id,
        arr="100",
        primary_finding_ref="primary_ref",
    )

    db.query.return_value.filter.return_value.first.return_value = primary
    lookup = build_primary_lookup_for_finding(db, secondary)

    assert "primary_ref" in lookup
    assert lookup["primary_ref"].id == primary.id
