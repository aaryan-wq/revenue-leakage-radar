from verification.context import AuditContext
from verification.financial import CONFIDENCE_MEDIUM
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "billing_frequency_mismatch"

INTERVAL_DAYS = {
    "monthly": 30,
    "month": 30,
    "quarterly": 90,
    "quarter": 90,
    "annual": 365,
    "yearly": 365,
    "year": 365,
}


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for invoice in ctx.invoices:
        if not invoice.subscription_id or not invoice.period_start or not invoice.period_end:
            continue

        sub = next((s for s in ctx.subscriptions if s.id == invoice.subscription_id), None)
        if not sub or not sub.billing_interval:
            continue

        period_days = (invoice.period_end - invoice.period_start).days
        expected_days = INTERVAL_DAYS.get(sub.billing_interval.lower(), 30)
        tolerance = max(5, int(expected_days * 0.1))

        if abs(period_days - expected_days) <= tolerance:
            continue

        loss = sub.price or 0
        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Billing frequency mismatch",
                severity="medium",
                confidence=CONFIDENCE_MEDIUM,
                customer_id=str(invoice.customer_id),
                subscription_id=str(sub.id),
                invoice_id=str(invoice.id),
                recommendation="Verify invoice billing period matches subscription interval.",
                evidence=[
                    EvidenceRecord(
                        field="billing_interval",
                        expected=sub.billing_interval,
                        actual=f"{period_days} day period",
                        reference_ids={"invoice": invoice.invoice_number},
                    )
                ],
            )
        )

    return findings
