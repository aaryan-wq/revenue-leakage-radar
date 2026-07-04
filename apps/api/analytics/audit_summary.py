"""Persist audit-level analytics summary fields for internal reporting."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy.orm import Session

from analytics.payloads import compute_data_presence, count_upload_files
from models import Audit
from verification.engine.registry import get_all_rules
from verification.recoverable import finding_recoverable_amount
from verification.types import RuleFinding, ScanReport


def _rule_category_lookup() -> dict[str, str]:
    return {module.spec.rule_id: module.spec.category for module in get_all_rules()}


def sync_upload_counts(db: Session, audit: Audit) -> None:
    csv_count, billing_count, crm_count = count_upload_files(audit)
    audit.csv_file_count = csv_count
    audit.billing_file_count = billing_count
    audit.crm_file_count = crm_count
    if csv_count > 0 and audit.upload_completed_at is None:
        audit.upload_completed_at = datetime.now(timezone.utc)
    db.flush()


def sync_data_presence(db: Session, audit: Audit) -> None:
    entities = audit.available_entities or []
    presence = compute_data_presence(entities)
    for key, value in presence.items():
        setattr(audit, key, value)
    if audit.crm_data_present and not audit.crm_platform_detected:
        audit.crm_platform_detected = "generic"
    if audit.platform:
        audit.billing_platform_detected = audit.platform
    db.flush()


def sync_billing_platform(db: Session, audit: Audit, platform: str | None) -> None:
    if platform:
        audit.platform = platform
        audit.billing_platform_detected = platform
    db.flush()


def mark_verification_started(db: Session, audit: Audit) -> None:
    audit.verification_started_at = datetime.now(timezone.utc)
    db.flush()


def apply_verification_summary(
    db: Session,
    audit: Audit,
    *,
    report: ScanReport,
    primary_findings: list[RuleFinding],
    secondary_count: int,
    coverage_score: Decimal | float | None,
    duration_ms: int,
) -> None:
    annual = sum_primary_arr(primary_findings)
    monthly = (annual / Decimal("12")).quantize(Decimal("0.01")) if annual else Decimal("0")

    audit.verification_completed_at = datetime.now(timezone.utc)
    audit.verification_duration_ms = duration_ms
    audit.rules_total = report.rules_total
    audit.rules_executed = report.rules_completed
    audit.rules_skipped = report.rules_skipped
    audit.rules_failed = report.rules_errored
    audit.findings_total = len(primary_findings)
    audit.estimated_annual_leakage = annual
    audit.estimated_monthly_leakage = monthly
    if coverage_score is not None:
        audit.coverage_score = Decimal(str(coverage_score))
    if report.overall_confidence is not None:
        audit.confidence_score = Decimal(report.overall_confidence)
    audit.top_rule_category = compute_top_rule_category(primary_findings)
    db.flush()


def sum_primary_arr(findings: list[RuleFinding]) -> Decimal:
    total = Decimal("0")
    for finding in findings:
        if finding.attribution != "primary":
            continue
        total += finding_recoverable_amount(finding)
    return total.quantize(Decimal("0.0001"))


def compute_top_rule_category(findings: list[RuleFinding]) -> str | None:
    if not findings:
        return None
    categories = _rule_category_lookup()
    totals: dict[str, Decimal] = defaultdict(lambda: Decimal("0"))
    for finding in findings:
        if finding.attribution != "primary":
            continue
        category = categories.get(finding.rule_id, "unknown")
        totals[category] += finding_recoverable_amount(finding)
    if not totals:
        return None
    return max(totals.items(), key=lambda item: item[1])[0]


def mark_checkout_started(db: Session, audit: Audit) -> None:
    audit.checkout_started_at = datetime.now(timezone.utc)
    db.flush()


def mark_checkout_completed(db: Session, audit: Audit, *, audit_type: str = "paid") -> None:
    audit.checkout_completed_at = datetime.now(timezone.utc)
    audit.audit_type = audit_type
    db.flush()


def mark_report_unlocked(db: Session, audit: Audit) -> None:
    audit.report_unlocked_at = datetime.now(timezone.utc)
    audit.audit_type = "paid"
    db.flush()


def mark_enterprise_interest(db: Session, audit: Audit) -> None:
    audit.enterprise_interest_flag = True
    audit.audit_type = "enterprise"
    db.flush()


def mark_anonymous_state(db: Session, audit: Audit) -> None:
    audit.is_anonymous = audit.clerk_user_id is None
    db.flush()


def link_user_updates(db: Session, audit: Audit, clerk_user_id: str) -> None:
    audit.clerk_user_id = clerk_user_id
    audit.is_anonymous = False
    db.flush()
