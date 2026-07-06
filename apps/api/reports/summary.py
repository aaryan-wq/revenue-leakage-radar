import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from core.canonical_entities import (
    CanonicalEntity,
    ENTITY_LABELS,
    TIER_3_OPTIONAL_ENTITIES,
    entities_from_uploaded_files,
)
from core.data_tiers import missing_recommended_entities
from core.enums import DataTier, FileType
from models import Audit, Customer, Finding, Invoice, Report
from reports.findings import (
    build_locked_preview,
    build_opportunity_breakdown,
    build_reconciliation,
    is_primary_finding,
    primary_findings,
    rule_lookup,
)
from verification.recoverable import finding_recoverable_amount


def _canonical_counts(db: Session, audit: Audit) -> dict[str, int]:
    report = audit.validation_report or {}
    counts = report.get("canonical_counts") or {}
    accounts = int(counts.get("customers") or 0)
    invoices = int(counts.get("invoices") or 0)

    if audit.company_id and (accounts == 0 or invoices == 0):
        if accounts == 0:
            accounts = db.query(Customer).filter(Customer.company_id == audit.company_id).count()
        if invoices == 0:
            customer_ids = [
                row[0] for row in db.query(Customer.id).filter(Customer.company_id == audit.company_id).all()
            ]
            if customer_ids:
                invoices = db.query(Invoice).filter(Invoice.customer_id.in_(customer_ids)).count()

    return {
        "accounts_reviewed": accounts,
        "invoices_reviewed": invoices,
    }


def _verification_checks(audit: Audit, findings: list[Finding]) -> list[dict[str, Any]]:
    scan_report = audit.scan_report or {}
    rule_logs = scan_report.get("rule_logs", [])
    lookup = rule_lookup()
    arr_by_rule: dict[str, Decimal] = {}
    excluded_arr_by_rule: dict[str, Decimal] = {}
    total_count_by_rule: dict[str, int] = {}
    primary_count_by_rule: dict[str, int] = {}

    for finding in findings:
        rule_id = finding.rule_id
        total_count_by_rule[rule_id] = total_count_by_rule.get(rule_id, 0) + 1
        amount = finding_recoverable_amount(finding)
        if is_primary_finding(finding):
            arr_by_rule[rule_id] = arr_by_rule.get(rule_id, Decimal("0")) + amount
            primary_count_by_rule[rule_id] = primary_count_by_rule.get(rule_id, 0) + 1
        else:
            excluded_arr_by_rule[rule_id] = excluded_arr_by_rule.get(rule_id, Decimal("0")) + amount

    checks: list[dict[str, Any]] = []
    for log in rule_logs:
        rule_id = log.get("rule_id", "")
        rule = lookup.get(rule_id)
        status = log.get("status", "skipped")
        total_count = total_count_by_rule.get(rule_id, log.get("finding_count", 0))
        primary_count = primary_count_by_rule.get(rule_id, 0)
        excluded_arr = excluded_arr_by_rule.get(rule_id, Decimal("0"))
        if status == "skipped":
            check_status = "not_run"
        elif status == "partial":
            check_status = "partial"
        elif status == "error":
            check_status = "error"
        elif total_count > 0:
            check_status = "issues_found"
        else:
            check_status = "passed"

        coverage_note = log.get("coverage_note")
        skip_reason = log.get("skip_reason")
        note = coverage_note or skip_reason
        if excluded_arr > 0 and primary_count < total_count:
            overlap_note = (
                f"{total_count - primary_count} overlapping secondary finding"
                f"{'s' if total_count - primary_count != 1 else ''} "
                f"({excluded_arr.quantize(Decimal('0.01'))} excluded from headline ARR)"
            )
            note = f"{note}. {overlap_note}" if note else overlap_note

        checks.append(
            {
                "rule_id": rule_id,
                "name": rule.name if rule else rule_id.replace("_", " ").title(),
                "status": check_status,
                "finding_count": total_count,
                "primary_finding_count": primary_count,
                "arr": str(arr_by_rule.get(rule_id, Decimal("0")).quantize(Decimal("0.01"))),
                "excluded_arr": str(excluded_arr.quantize(Decimal("0.01"))) if excluded_arr > 0 else None,
                "skip_reason": skip_reason,
                "coverage_note": note,
            }
        )
    return checks


def _build_coverage(audit: Audit) -> dict[str, Any]:
    if audit.available_entities:
        available_entities = {CanonicalEntity(entity) for entity in audit.available_entities}
    else:
        uploaded_types: set[FileType] = set()
        if audit.uploaded_file_types:
            for ft in audit.uploaded_file_types:
                try:
                    uploaded_types.add(FileType(ft))
                except ValueError:
                    continue
        available_entities = entities_from_uploaded_files(uploaded_types)

    billing_uploaded = sorted(
        (
            ENTITY_LABELS.get(entity, entity.value)
            for entity in available_entities
            if entity not in TIER_3_OPTIONAL_ENTITIES
        ),
        key=str,
    )
    billing_missing = [
        ENTITY_LABELS.get(entity, entity.value)
        for entity in missing_recommended_entities(available_entities)
    ]
    crm_uploaded = sorted(
        (
            ENTITY_LABELS.get(entity, entity.value)
            for entity in available_entities
            if entity in TIER_3_OPTIONAL_ENTITIES
        ),
        key=str,
    )
    crm_present = any(entity in available_entities for entity in TIER_3_OPTIONAL_ENTITIES)

    data_tier = audit.data_tier or DataTier.TIER_0.value
    impacts: list[str] = []

    if data_tier == DataTier.TIER_0.value:
        impacts.append(
            "Tier 0 only: core pricing rules run, but subscription and invoice-level checks are limited."
        )
    if billing_missing:
        missing_labels = ", ".join(billing_missing)
        impacts.append(f"Missing recommended entities: {missing_labels}.")
    if not crm_present:
        impacts.append("No CRM data present, contract and seat-count rules will not run.")
    if not impacts:
        impacts.append("Strong data coverage, recommended entities present for maximum rule execution.")

    return {
        "data_tier": data_tier,
        "billing_files_uploaded": billing_uploaded,
        "billing_files_missing": billing_missing,
        "crm_files_uploaded": crm_uploaded,
        "crm_present": crm_present,
        "confidence_impact": " ".join(impacts),
    }


def build_free_summary(
    db: Session,
    audit: Audit,
    *,
    findings: list[Finding] | None = None,
) -> dict[str, Any]:
    report = db.query(Report).filter(Report.audit_id == audit.id).first()
    if not report:
        raise ValueError("Report not found for audit")

    if findings is None:
        findings = db.query(Finding).filter(Finding.audit_id == audit.id).all()
    scan_report = audit.scan_report or {}
    counts = _canonical_counts(db, audit)
    recoverable = report.recoverable_arr
    confidence = report.confidence

    return {
        "audit_id": str(audit.id),
        "report_id": str(report.id),
        "recoverable_arr": str(recoverable),
        "confidence": str(confidence) if confidence is not None else None,
        "finding_count": report.finding_count,
        "accounts_reviewed": counts["accounts_reviewed"],
        "invoices_reviewed": counts["invoices_reviewed"],
        "rules_completed": scan_report.get("rules_completed", 0),
        "rules_total": scan_report.get("rules_total", 0),
        "opportunity_breakdown": build_opportunity_breakdown(findings),
        "reconciliation": build_reconciliation(findings, recoverable),
        "verification_checks": _verification_checks(audit, findings),
        "locked_preview": build_locked_preview(findings),
        "coverage": _build_coverage(audit),
        "purchased": report.purchased,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
    }


def get_audit_summary(db: Session, audit_id: uuid.UUID) -> dict[str, Any]:
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise ValueError("Audit not found")
    if audit.status != "completed":
        raise ValueError("Audit scan is not complete")
    return build_free_summary(db, audit)
