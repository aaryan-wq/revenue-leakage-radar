import json
import uuid
from decimal import Decimal

from models import Finding
from verification.types import RuleFinding


def rule_finding_to_orm(audit_id: uuid.UUID, finding: RuleFinding) -> Finding:
    return Finding(
        audit_id=audit_id,
        rule_id=finding.rule_id,
        severity=finding.severity,
        confidence=finding.confidence,
        customer_id=uuid.UUID(finding.customer_id) if finding.customer_id else None,
        invoice_id=uuid.UUID(finding.invoice_id) if finding.invoice_id else None,
        subscription_id=uuid.UUID(finding.subscription_id) if finding.subscription_id else None,
        estimated_monthly_loss=finding.estimated_monthly_loss,
        estimated_arr_loss=finding.estimated_arr_loss,
        recommendation=finding.recommendation,
        evidence=json.dumps(finding.evidence_json()),
    )


def serialize_findings_for_report(findings: list[Finding]) -> dict:
    return {
        "count": len(findings),
        "recoverable_arr": str(sum((f.estimated_arr_loss for f in findings), Decimal("0"))),
    }
