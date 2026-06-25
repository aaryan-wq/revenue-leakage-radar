import logging
import time
import uuid
from decimal import Decimal

from sqlalchemy.orm import Session

from audit.service import transition_audit_status
from core.enums import AuditStatus
from findings.service import clear_findings, persist_findings
from models import Audit
from reports.service import upsert_report
from verification.context import load_audit_context
from verification.financial import weighted_confidence
from verification.registry import RuleDefinition, get_all_rules
from verification.types import RuleExecutionLog, RuleFinding, ScanReport

logger = logging.getLogger(__name__)


def _should_skip_rule(rule: RuleDefinition, ctx) -> str | None:
    if rule.requires_crm and not ctx.has_crm:
        return "CRM data not available"
    if rule.requires_credit_data and not ctx.has_credit_data:
        return "Credit amount data not present in invoices"
    if rule.requires_manual_override and not ctx.has_manual_override_data:
        return "Manual override flags not present in line items"
    if rule.evaluate is None:
        return "Rule evaluator not configured"
    return None


def run_verification_engine(db: Session, audit: Audit) -> ScanReport:
    if not audit.company_id:
        raise ValueError("Audit has no company_id — run ingestion first")

    transition_audit_status(db, audit, AuditStatus.SCANNING)
    audit.scan_error = None
    db.commit()

    ctx = load_audit_context(db, audit.id, audit.company_id)
    rules = get_all_rules()
    all_findings: list[RuleFinding] = []
    logs: list[RuleExecutionLog] = []
    skipped = 0

    for rule in rules:
        start = time.perf_counter()
        skip_reason = _should_skip_rule(rule, ctx)
        if skip_reason:
            skipped += 1
            logs.append(
                RuleExecutionLog(
                    rule_id=rule.rule_id,
                    status="skipped",
                    skip_reason=skip_reason,
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
            )
            continue

        try:
            findings = rule.evaluate(ctx)
            duration_ms = int((time.perf_counter() - start) * 1000)
            all_findings.extend(findings)
            logs.append(
                RuleExecutionLog(
                    rule_id=rule.rule_id,
                    status="ran",
                    finding_count=len(findings),
                    duration_ms=duration_ms,
                )
            )
        except Exception as exc:
            logger.exception("Rule %s failed for audit %s", rule.rule_id, audit.id)
            logs.append(
                RuleExecutionLog(
                    rule_id=rule.rule_id,
                    status="error",
                    error=str(exc),
                    duration_ms=int((time.perf_counter() - start) * 1000),
                )
            )

    transition_audit_status(db, audit, AuditStatus.GENERATING_REPORT)

    clear_findings(db, audit.id)
    orm_findings = persist_findings(db, audit.id, all_findings)

    recoverable = sum((f.estimated_arr_loss for f in orm_findings), Decimal("0"))
    overall_conf = weighted_confidence(orm_findings)
    upsert_report(db, audit.id, recoverable, len(orm_findings), overall_conf)

    scan_report = ScanReport(
        rules_total=len(rules),
        rules_completed=len(rules) - skipped,
        rules_skipped=skipped,
        finding_count=len(orm_findings),
        recoverable_arr=str(recoverable),
        overall_confidence=str(overall_conf) if overall_conf else None,
        rule_logs=logs,
    )
    audit.scan_report = scan_report.to_dict()
    transition_audit_status(db, audit, AuditStatus.COMPLETED)
    audit.scan_error = None
    db.commit()

    logger.info(
        "Verification complete for audit %s: %d findings, ARR %s",
        audit.id,
        len(orm_findings),
        recoverable,
    )
    return scan_report


def run_verification_pipeline(db: Session, audit_id: uuid.UUID) -> None:
    audit = db.query(Audit).filter(Audit.id == audit_id).first()
    if not audit:
        raise ValueError(f"Audit not found: {audit_id}")

    try:
        run_verification_engine(db, audit)
    except Exception as exc:
        logger.exception("Verification failed for audit %s", audit_id)
        audit.scan_error = "Verification scan failed. Please try again."
        transition_audit_status(db, audit, AuditStatus.PROCESSING_FAILED)
        db.commit()
        raise exc
