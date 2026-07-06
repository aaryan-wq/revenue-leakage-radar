import uuid
from decimal import Decimal
from unittest.mock import MagicMock, patch

from models import Audit, Finding, Report
from reports.exports import build_evidence_csv, build_findings_csv
from reports.pdf import (
    _finding_anchor,
    _group_findings_by_category,
    _prepare_findings_for_report,
    build_report_pdf,
)


def _report_bundle():
    audit_id = uuid.uuid4()
    report_id = uuid.uuid4()
    audit = Audit(session_token="token", status="completed")
    audit.id = audit_id
    audit.validation_report = {"canonical_counts": {"customers": 2, "invoices": 5}}
    audit.scan_report = {"rules_completed": 5, "rules_total": 5, "rule_logs": []}
    report = Report(
        id=report_id,
        audit_id=audit_id,
        recoverable_arr=Decimal("5000"),
        finding_count=1,
        confidence=Decimal("90"),
        purchased=True,
    )
    finding = Finding(
        id=uuid.uuid4(),
        audit_id=audit_id,
        rule_id="expired_discount",
        severity="high",
        confidence=Decimal("90"),
        estimated_monthly_loss=Decimal("400"),
        estimated_arr_loss=Decimal("5000"),
        recommendation="Remove expired discount",
        evidence='{"records": []}',
    )
    return audit, report, finding


def test_build_findings_csv_contains_headers():
    audit, report, finding = _report_bundle()
    db = MagicMock()
    db.query.return_value.filter.return_value.order_by.return_value.all.return_value = [finding]

    with patch("reports.exports.EntityIdResolver.for_findings", return_value=MagicMock()), patch(
        "reports.exports.build_primary_finding_lookup", return_value={}
    ), patch(
        "reports.exports.serialize_finding",
        return_value={
            "id": str(finding.id),
            "rule_id": finding.rule_id,
            "title": "Expired Discount",
            "category": "discounts",
            "severity": "high",
            "confidence": "90",
            "estimated_monthly_loss": "400",
            "estimated_arr_loss": "5000",
            "customer_id": None,
            "subscription_id": None,
            "invoice_id": None,
            "recommendation": "Fix",
        },
    ):
        content = build_findings_csv(db, report)

    text = content.decode("utf-8")
    assert "rule_id" in text
    assert "expired_discount" in text


def test_build_evidence_csv_contains_headers():
    audit, report, finding = _report_bundle()
    finding.evidence = '{"records": [{"field": "price", "expected": "100", "actual": "80"}]}'
    db = MagicMock()
    db.query.return_value.filter.return_value.all.return_value = [finding]

    content = build_evidence_csv(db, report)

    text = content.decode("utf-8")
    assert "finding_id" in text
    assert "expected" in text
    assert "price" in text


def test_build_report_pdf_returns_bytes():
    audit, report, finding = _report_bundle()
    db = MagicMock()

    detail = {
        "id": str(report.id),
        "audit_id": str(audit.id),
        "purchased": True,
        "generated_at": "2026-06-01T12:00:00",
        "company_name": "Acme Corp",
        "executive_summary": {
            "recoverable_arr": "5000",
            "high_confidence_arr": "5000",
            "medium_confidence_arr": "0",
            "low_confidence_arr": "0",
            "accounts_reviewed": 2,
            "invoices_reviewed": 5,
            "finding_count": 1,
            "confidence": "90",
            "rules_completed": 5,
            "rules_total": 5,
            "narrative": "Executive narrative.",
            "reconciliation": {
                "secondary_excluded_arr": "250.00",
            },
        },
        "opportunity_breakdown": [
            {
                "category": "discounts",
                "label": "Expired Discounts",
                "arr": "5000",
                "confidence": "90",
                "issue_count": 1,
                "account_count": 1,
            }
        ],
        "verification_checks": [
            {
                "rule_id": "expired_discount",
                "name": "Expired Discount Still Applied",
                "status": "issues_found",
                "finding_count": 1,
                "arr": "5000",
                "skip_reason": None,
                "coverage_note": None,
            }
        ],
        "findings": [
            {
                "id": str(finding.id),
                "rule_id": "expired_discount",
                "title": "Expired Discount Still Applied",
                "category": "discounts",
                "category_label": "Expired Discounts",
                "severity": "high",
                "confidence": "90",
                "estimated_monthly_loss": "400",
                "estimated_arr_loss": "5000",
                "customer_id": "cust_123",
                "subscription_id": "sub_456",
                "invoice_id": None,
                "recommendation": "Remove expired discount from subscription.",
                "evidence_records": [
                    {
                        "field": "discount_end_date",
                        "expected": "2025-01-01",
                        "actual": "still applied",
                        "reference_ids": {"subscription_id": "sub_456"},
                    }
                ],
            }
        ],
    }

    with patch("reports.pdf.build_report_detail", return_value=detail) as mock_detail:
        pdf_bytes = build_report_pdf(db, report)

    mock_detail.assert_called_once_with(db, report, evidence_record_limit=None, include_findings=True)

    assert pdf_bytes.startswith(b"%PDF")
    assert len(pdf_bytes) > 2_000


def test_finding_anchor_is_pdf_safe():
    anchor = _finding_anchor("a1b2c3d4-e5f6-7890-abcd-ef1234567890")
    assert anchor == "finding_a1b2c3d4e5f67890abcdef1234567890"
    assert "-" not in anchor


def test_group_findings_by_category_sorts_by_primary_recoverable():
    findings = _prepare_findings_for_report(
        [
            {
                "id": "1",
                "category_label": "Expired Discounts",
                "recoverable_amount": "100",
                "attribution": "primary",
            },
            {
                "id": "2",
                "category_label": "Legacy Pricing",
                "recoverable_amount": "500",
                "attribution": "primary",
            },
            {
                "id": "3",
                "category_label": "Expired Discounts",
                "recoverable_amount": "300",
                "attribution": "primary",
            },
        ]
    )
    grouped = _group_findings_by_category(findings)
    assert grouped[0][0] == "Legacy Pricing"
    assert grouped[1][0] == "Expired Discounts"
    assert grouped[1][1][0]["id"] == "3"
