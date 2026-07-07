"""High-level analytics tracking helpers for backend system events."""

from __future__ import annotations

import time
from collections import defaultdict
from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from analytics import audit_summary, events
from analytics.client import capture
from analytics.payloads import audit_distinct_id, audit_lifecycle_properties, upload_file_properties
from models import Audit
from verification.engine.registry import get_all_rules
from verification.recoverable import finding_recoverable_amount
from verification.types import RuleFinding, ScanReport


def track(audit: Audit | None, event: str, properties: dict[str, Any] | None = None) -> None:
    props = dict(properties or {})
    if audit is not None:
        props = {**audit_lifecycle_properties(audit), **props}
    distinct_id = audit_distinct_id(audit) if audit is not None else "system"
    capture(event, distinct_id=distinct_id, properties=props)


def track_audit_created(audit: Audit) -> None:
    track(audit, events.AUDIT_SESSION_CREATED)
    track(audit, events.AUDIT_STARTED)


def track_audit_cancelled(audit: Audit) -> None:
    track(audit, events.AUDIT_CANCELLED)


def track_upload_completed(
    audit: Audit,
    *,
    file_id: str,
    original_filename: str,
    detected_file_type: str,
    file_size_bytes: int,
    replaced: bool = False,
    detection_source: str | None = None,
) -> None:
    event = events.CSV_REPLACED if replaced else events.CSV_UPLOAD_COMPLETED
    capture(
        event,
        distinct_id=audit_distinct_id(audit),
        properties=upload_file_properties(
            audit,
            file_id=file_id,
            original_filename=original_filename,
            detected_file_type=detected_file_type,
            file_size_bytes=file_size_bytes,
            replaced=replaced,
            detection_source=detection_source,
        ),
    )


def track_upload_removed(audit: Audit, *, file_id: str, original_filename: str) -> None:
    track(
        audit,
        events.CSV_REMOVED,
        {"file_id": file_id, "original_filename": original_filename},
    )


def track_validation_started(audit: Audit) -> None:
    track(audit, events.CSV_VALIDATION_STARTED)


def track_validation_completed(audit: Audit) -> None:
    track(audit, events.CSV_VALIDATION_COMPLETED, {"validation_result": audit.validation_result})


def track_validation_failed(audit: Audit, *, reason: str | None = None) -> None:
    track(audit, events.CSV_VALIDATION_FAILED, {"failure_reason": reason})


def _rule_lookup() -> dict[str, tuple[str, str]]:
    return {module.spec.rule_id: (module.spec.name, module.spec.category) for module in get_all_rules()}


def _rule_leakage_totals(findings: list[RuleFinding]) -> dict[str, tuple[int, Decimal, Decimal]]:
    totals: dict[str, tuple[int, Decimal, Decimal]] = defaultdict(lambda: (0, Decimal("0"), Decimal("0")))
    for finding in findings:
        if finding.attribution != "primary":
            continue
        count, monthly, annual = totals[finding.rule_id]
        monthly += finding.estimated_monthly_loss or Decimal("0")
        annual += finding_recoverable_amount(finding)
        totals[finding.rule_id] = (count + 1, monthly, annual)
    return totals


def track_verification_started(audit: Audit) -> float:
    track(audit, events.VERIFICATION_STARTED)
    return time.perf_counter()


def track_verification_completed(
    db: Session,
    audit: Audit,
    *,
    report: ScanReport,
    primary_findings: list[RuleFinding],
    secondary_count: int,
    coverage_score: float | Decimal | None,
    started_at: float,
) -> None:
    duration_ms = int((time.perf_counter() - started_at) * 1000)
    audit_summary.apply_verification_summary(
        db,
        audit,
        report=report,
        primary_findings=primary_findings,
        secondary_count=secondary_count,
        coverage_score=coverage_score,
        duration_ms=duration_ms,
    )

    rule_meta = _rule_lookup()
    leakage_by_rule = _rule_leakage_totals(primary_findings)

    for log in report.rule_logs:
        name, category = rule_meta.get(log.rule_id, (log.rule_id, "unknown"))
        if log.status == "skipped":
            track(
                audit,
                events.RULE_SKIPPED,
                {"rule_id": log.rule_id, "skip_reason": log.skip_reason or log.coverage_note},
            )
        elif log.status == "error":
            track(
                audit,
                events.RULE_FAILED,
                {"rule_id": log.rule_id, "error": log.error},
            )
        else:
            count, monthly, annual = leakage_by_rule.get(log.rule_id, (0, Decimal("0"), Decimal("0")))
            track(
                audit,
                events.RULE_EXECUTED,
                {
                    "rule_id": log.rule_id,
                    "rule_name": name,
                    "rule_category": category,
                    "findings_count": count or log.finding_count,
                    "monthly_leakage_total": float(monthly),
                    "annual_leakage_total": float(annual),
                    "execution_duration_ms": log.duration_ms,
                },
            )

    if primary_findings:
        track(
            audit,
            events.FINDING_CREATED,
            {"findings_count": len(primary_findings)},
        )
    if secondary_count:
        track(audit, events.FINDING_SUPPRESSED, {"findings_count": secondary_count})

    if coverage_score is not None:
        track(audit, events.COVERAGE_SCORE_CALCULATED, {"coverage_score": float(coverage_score)})

    track(
        audit,
        events.VERIFICATION_COMPLETED,
        {
            "verification_duration_ms": duration_ms,
            "rules_total": report.rules_total,
            "rules_executed": report.rules_completed,
            "rules_skipped": report.rules_skipped,
            "rules_failed": report.rules_errored,
            "findings_total": len(primary_findings),
            "estimated_monthly_leakage": float(audit.estimated_monthly_leakage or 0),
            "estimated_annual_leakage": float(audit.estimated_annual_leakage or 0),
            "coverage_score": float(coverage_score) if coverage_score is not None else None,
            "confidence_score": float(audit.confidence_score) if audit.confidence_score is not None else None,
        },
    )
    track(audit, events.AUDIT_COMPLETED)


def track_verification_failed(audit: Audit, *, error: str | None = None) -> None:
    track(audit, events.VERIFICATION_FAILED, {"error": error})
    track(audit, events.AUDIT_FAILED, {"stage": "verification", "error": error})


def track_checkout_started(
    audit: Audit,
    *,
    checkout_type: str,
    price_usd: float | None = None,
    currency: str | None = None,
) -> None:
    track(
        audit,
        events.CHECKOUT_STARTED,
        {
            "checkout_type": checkout_type,
            "price_usd": price_usd,
            "currency": currency,
            "payment_provider": "stripe",
            "estimated_annual_leakage_at_checkout": float(audit.estimated_annual_leakage or 0),
            "findings_total_at_checkout": audit.findings_total,
        },
    )


def track_checkout_completed(
    audit: Audit,
    *,
    checkout_type: str,
    price_usd: float | None = None,
    currency: str | None = None,
) -> None:
    track(
        audit,
        events.CHECKOUT_COMPLETED,
        {
            "checkout_type": checkout_type,
            "price_usd": price_usd,
            "currency": currency,
            "payment_provider": "stripe",
            "estimated_annual_leakage_at_checkout": float(audit.estimated_annual_leakage or 0),
            "findings_total_at_checkout": audit.findings_total,
        },
    )


def track_report_unlocked(audit: Audit, *, checkout_type: str = "single_report") -> None:
    track(
        audit,
        events.REPORT_ACCESS_UNLOCKED,
        {
            "checkout_type": checkout_type,
            "findings_total": audit.findings_total,
            "estimated_annual_leakage": float(audit.estimated_annual_leakage or 0),
        },
    )


def track_report_viewed(audit: Audit, *, user_id: str | None = None) -> None:
    track(
        audit,
        events.PAID_REPORT_VIEWED,
        {
            "user_id": user_id or audit.clerk_user_id,
            "findings_total": audit.findings_total,
            "estimated_annual_leakage": float(audit.estimated_annual_leakage or 0),
        },
    )


def track_finding_viewed(audit: Audit, *, finding_id: str, user_id: str | None = None) -> None:
    track(
        audit,
        events.FINDING_DETAIL_VIEWED,
        {
            "finding_id": finding_id,
            "user_id": user_id or audit.clerk_user_id,
            "findings_total": audit.findings_total,
            "estimated_annual_leakage": float(audit.estimated_annual_leakage or 0),
        },
    )


def track_report_exported(audit: Audit, *, export_format: str, user_id: str | None = None) -> None:
    event = {
        "pdf": events.REPORT_EXPORTED_PDF,
        "csv": events.REPORT_EXPORTED_CSV,
        "evidence": events.REPORT_EXPORTED_CSV,
    }.get(export_format, events.REPORT_EXPORTED_CSV)
    track(
        audit,
        event,
        {
            "user_id": user_id or audit.clerk_user_id,
            "export_format": export_format,
            "findings_total": audit.findings_total,
            "estimated_annual_leakage": float(audit.estimated_annual_leakage or 0),
        },
    )
