import uuid
from typing import Any

from sqlalchemy.orm import Session

from ai.summaries import generate_executive_narrative
from models import Audit, Finding, Report
from reports.entity_ids import EntityIdResolver
from reports.findings import (
    build_primary_finding_lookup,
    serialize_finding,
    sum_arr_by_confidence_band,
)
from reports.summary import build_free_summary


def build_report_detail(
    db: Session,
    report: Report,
    *,
    evidence_record_limit: int | None = 3,
) -> dict[str, Any]:
    audit = db.query(Audit).filter(Audit.id == report.audit_id).first()
    if not audit:
        raise ValueError("Audit not found")

    findings = (
        db.query(Finding)
        .filter(Finding.audit_id == audit.id)
        .order_by(Finding.estimated_arr_loss.desc())
        .all()
    )
    summary = build_free_summary(db, audit, findings=findings)
    confidence_bands = sum_arr_by_confidence_band(findings)
    narrative = generate_executive_narrative(summary)
    entity_resolver = EntityIdResolver.for_findings(db, findings)
    primary_by_ref = build_primary_finding_lookup(findings)

    return {
        "id": str(report.id),
        "audit_id": str(audit.id),
        "purchased": report.purchased,
        "generated_at": report.generated_at.isoformat() if report.generated_at else None,
        "company_name": audit.company.name if audit.company else None,
        "executive_summary": {
            "recoverable_arr": summary["recoverable_arr"],
            "high_confidence_arr": confidence_bands["high"],
            "medium_confidence_arr": confidence_bands["medium"],
            "low_confidence_arr": confidence_bands["low"],
            "accounts_reviewed": summary["accounts_reviewed"],
            "invoices_reviewed": summary["invoices_reviewed"],
            "finding_count": summary["finding_count"],
            "confidence": summary["confidence"],
            "rules_completed": summary["rules_completed"],
            "rules_total": summary["rules_total"],
            "narrative": narrative,
            "reconciliation": summary.get("reconciliation"),
        },
        "opportunity_breakdown": summary["opportunity_breakdown"],
        "verification_checks": summary["verification_checks"],
        "findings": [
            serialize_finding(
                f,
                include_evidence=True,
                evidence_record_limit=evidence_record_limit,
                entity_resolver=entity_resolver,
                primary_by_ref=primary_by_ref,
            )
            for f in findings
        ],
    }
