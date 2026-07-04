import json
import uuid
from decimal import Decimal

from models import Finding
from verification.attribution import sum_primary_recoverable_arr
from verification.types import RuleFinding


def rule_finding_to_orm(audit_id: uuid.UUID, finding: RuleFinding) -> Finding:
    return Finding(
        audit_id=audit_id,
        rule_id=finding.rule_id,
        rule_name=finding.rule_name,
        severity=finding.severity,
        confidence=finding.confidence,
        status=finding.status,
        customer_id=uuid.UUID(finding.customer_id) if finding.customer_id else None,
        invoice_id=uuid.UUID(finding.invoice_id) if finding.invoice_id else None,
        subscription_id=uuid.UUID(finding.subscription_id) if finding.subscription_id else None,
        product_id=finding.product_id,
        expected_value=finding.expected_value,
        actual_value=finding.actual_value,
        difference=finding.delta,
        estimated_monthly_loss=finding.estimated_monthly_loss,
        estimated_arr_loss=finding.estimated_arr_loss,
        recommendation=finding.recommendation,
        evidence=json.dumps(finding.evidence_json()),
        calculation_trace=json.dumps(
            finding.calculation_trace.model_dump(mode="json")
        )
        if finding.calculation_trace
        else None,
        leak_family=finding.leak_family,
        attribution=finding.attribution or "primary",
        primary_finding_ref=finding.primary_finding_ref,
        finding_ref=finding.finding_ref,
        rule_version=finding.rule_version,
    )


def serialize_findings_for_report(findings: list[Finding]) -> dict:
    return {
        "count": len(findings),
        "recoverable_arr": str(sum_primary_recoverable_arr_from_orm(findings)),
    }


def sum_primary_recoverable_arr_from_orm(findings: list[Finding]) -> Decimal:
    from verification.recoverable import finding_recoverable_amount

    total = Decimal("0")
    for finding in findings:
        if finding.attribution != "primary":
            continue
        total += finding_recoverable_amount(finding)
    return total.quantize(Decimal("0.0001"))
