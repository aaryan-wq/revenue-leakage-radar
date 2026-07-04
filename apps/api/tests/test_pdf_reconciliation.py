"""PDF and summary tables must use the same recoverable amount semantics."""

from __future__ import annotations

import uuid
from decimal import Decimal

from models import Audit, Finding
from reports.findings import build_opportunity_breakdown, serialize_finding
from reports.pdf import (
    _group_findings_by_category,
    _prepare_findings_for_report,
    _primary_recoverable_amount,
    _recoverable_amount,
)
from reports.summary import _verification_checks
from verification.recoverable import finding_recoverable_amount


def _finding(
    *,
    rule_id: str = "credit_leakage",
    monthly: str = "500",
    annual: str = "0",
    semantics: str = "one_time",
    attribution: str = "primary",
) -> Finding:
    evidence = {
        "records": [],
        "leakage_computation": {
            "semantics": semantics,
            "unit_expected": "0",
            "unit_actual": monthly,
            "quantity": 1,
            "billing_interval": "monthly",
            "monthly_loss": monthly,
            "annual_loss": annual,
            "formula": "Recoverable amount",
        },
    }
    import json

    return Finding(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        rule_id=rule_id,
        severity="medium",
        confidence=Decimal("70"),
        estimated_monthly_loss=Decimal(monthly),
        estimated_arr_loss=Decimal(annual),
        recommendation="Fix",
        evidence=json.dumps(evidence),
        attribution=attribution,
    )


def test_one_time_credit_leakage_uses_monthly_as_recoverable():
    finding = _finding()
    assert finding_recoverable_amount(finding) == Decimal("500")
    payload = serialize_finding(finding)
    assert payload["recoverable_amount"] in ("500", "500.00")
    assert payload["leakage_semantics"] == "one_time"


def test_prepare_findings_assigns_stable_report_index():
    findings = [
        {
            "id": "low",
            "category_label": "Legacy Pricing",
            "recoverable_amount": "100",
            "attribution": "primary",
        },
        {
            "id": "high",
            "category_label": "Invoice Errors",
            "recoverable_amount": "500",
            "attribution": "primary",
        },
    ]
    prepared = _prepare_findings_for_report(findings)
    assert prepared[0]["id"] == "high"
    assert prepared[0]["report_index"] == 1
    assert prepared[1]["report_index"] == 2


def test_group_findings_category_total_counts_primary_recoverable_only():
    prepared = _prepare_findings_for_report(
        [
            {
                "id": "1",
                "category_label": "Expired Discounts",
                "recoverable_amount": "100",
                "attribution": "primary",
            },
            {
                "id": "2",
                "category_label": "Expired Discounts",
                "recoverable_amount": "300",
                "attribution": "secondary",
            },
            {
                "id": "3",
                "category_label": "Legacy Pricing",
                "recoverable_amount": "500",
                "attribution": "primary",
            },
        ]
    )
    grouped = dict(_group_findings_by_category(prepared))
    assert sum(_primary_recoverable_amount(row) for row in grouped["Expired Discounts"]) == 100.0
    assert sum(_primary_recoverable_amount(row) for row in grouped["Legacy Pricing"]) == 500.0


def test_opportunity_breakdown_matches_one_time_recoverable():
    findings = [
        _finding(rule_id="credit_leakage", monthly="500", annual="0", semantics="one_time"),
        _finding(
            rule_id="duplicate_credit",
            monthly="50",
            annual="600",
            semantics="recurring_run_rate",
        ),
    ]
    breakdown = build_opportunity_breakdown(findings)
    credits = next(row for row in breakdown if row["label"] == "Credit Adjustments")
    assert credits["arr"] == "1100.00"


def test_verification_checks_explain_secondary_overlap():
    audit = Audit(session_token="token", status="completed")
    audit.scan_report = {
        "rule_logs": [
            {"rule_id": "duplicate_discount", "status": "ran", "finding_count": 1},
        ]
    }
    findings = [
        Finding(
            id=uuid.uuid4(),
            audit_id=uuid.uuid4(),
            rule_id="duplicate_discount",
            severity="high",
            confidence=Decimal("85"),
            estimated_monthly_loss=Decimal("332.47"),
            estimated_arr_loss=Decimal("3989.64"),
            recommendation="Fix",
            evidence='{"records": []}',
            attribution="secondary",
        )
    ]
    checks = _verification_checks(audit, findings)
    assert checks[0]["finding_count"] == 1
    assert checks[0]["primary_finding_count"] == 0
    assert checks[0]["arr"] == "0.00"
    assert checks[0]["excluded_arr"] == "3989.64"
    assert "overlapping secondary finding" in (checks[0]["coverage_note"] or "")
