import uuid
from decimal import Decimal
from unittest.mock import MagicMock

import pytest

from models import Audit, Finding, Report
from reports.findings import build_opportunity_breakdown, build_locked_preview, serialize_finding
from reports.summary import build_free_summary


def _finding(rule_id: str, arr: str, category_rule: str = "expired_discount") -> Finding:
    return Finding(
        id=uuid.uuid4(),
        audit_id=uuid.uuid4(),
        rule_id=category_rule,
        severity="high",
        confidence=Decimal("85"),
        estimated_monthly_loss=Decimal(arr) / Decimal("12"),
        estimated_arr_loss=Decimal(arr),
        recommendation="Review billing",
        evidence='{"records": [{"field": "price", "expected": "100", "actual": "80"}]}',
    )


def test_build_opportunity_breakdown_groups_by_category():
    findings = [
        _finding("a", "12000", "expired_discount"),
        _finding("b", "8000", "legacy_pricing_pre_catalog"),
        _finding("c", "4000", "expired_discount"),
    ]
    breakdown = build_opportunity_breakdown(findings)
    assert len(breakdown) == 2
    assert breakdown[0]["arr"] == "16000.00" or breakdown[0]["issue_count"] >= 1


def test_build_locked_preview_limits_to_three():
    findings = [_finding(str(i), str(1000 * (i + 1))) for i in range(5)]
    preview = build_locked_preview(findings, limit=3)
    assert len(preview) == 3
    assert "title" in preview[0]
    assert "arr" in preview[0]


def test_serialize_finding_parses_evidence():
    finding = _finding("x", "5000")
    payload = serialize_finding(finding)
    assert payload["title"]
    assert len(payload["evidence_records"]) == 1


def test_build_free_summary_aggregates_metrics():
    audit_id = uuid.uuid4()
    report_id = uuid.uuid4()

    audit = Audit(session_token="token", status="completed")
    audit.id = audit_id
    audit.validation_report = {"canonical_counts": {"customers": 10, "invoices": 50}}
    audit.uploaded_file_types = ["invoice_line_items", "price_catalog"]
    audit.data_tier = "tier_0"
    audit.scan_report = {
        "rules_completed": 18,
        "rules_total": 20,
        "rule_logs": [
            {"rule_id": "expired_discount", "status": "ran", "finding_count": 1},
        ],
    }

    report = Report(
        id=report_id,
        audit_id=audit_id,
        recoverable_arr=Decimal("12000"),
        finding_count=1,
        confidence=Decimal("88"),
        purchased=False,
    )
    findings = [_finding("a", "12000")]

    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = report
    db.query.return_value.filter.return_value.all.return_value = findings

    summary = build_free_summary(db, audit)
    assert summary["recoverable_arr"] == "12000"
    assert summary["finding_count"] == 1
    assert summary["accounts_reviewed"] == 10
    assert summary["invoices_reviewed"] == 50
    assert len(summary["locked_preview"]) == 1
    assert summary["purchased"] is False
    assert "coverage" in summary
    assert summary["coverage"]["data_tier"] == "tier_0"
    assert "Subscription" in summary["coverage"]["billing_files_missing"]


def test_build_coverage_includes_crm_impact():
    from reports.summary import _build_coverage

    audit = Audit(session_token="token", status="completed")
    audit.uploaded_file_types = ["invoice_line_items", "price_catalog", "crm_contracts"]
    audit.data_tier = "tier_2_plus"
    coverage = _build_coverage(audit)
    assert coverage["crm_present"] is True
    assert "Contract" in coverage["crm_files_uploaded"]


def test_verification_checks_map_partial_status():
    from reports.summary import _verification_checks

    audit = Audit(session_token="token", status="completed")
    audit.scan_report = {
        "rule_logs": [
            {
                "rule_id": "price_catalog_mismatch",
                "status": "partial",
                "finding_count": 2,
                "coverage_note": "Running with reduced coverage; missing: invoices",
            }
        ]
    }
    checks = _verification_checks(audit, [])
    assert checks[0]["status"] == "partial"
    assert checks[0]["coverage_note"] == "Running with reduced coverage; missing: invoices"


def test_verification_checks_unknown_rule_id_uses_humanized_name():
    from reports.summary import _verification_checks

    audit = Audit(session_token="token", status="completed")
    audit.scan_report = {
        "rule_logs": [
            {"rule_id": "custom_unknown_rule", "status": "skipped", "finding_count": 0},
        ]
    }
    checks = _verification_checks(audit, [])
    assert checks[0]["name"] == "Custom Unknown Rule"
