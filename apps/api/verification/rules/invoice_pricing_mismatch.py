from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "invoice_subscription_price_mismatch"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for li in ctx.line_items:
        if li.unit_price is None:
            continue
        invoice = next((i for i in ctx.invoices if i.id == li.invoice_id), None)
        if not invoice or not invoice.subscription_id:
            continue

        sub = next((s for s in ctx.subscriptions if s.id == invoice.subscription_id), None)
        if not sub or sub.price is None:
            continue
        if li.unit_price == sub.price:
            continue

        monthly, annual = compute_leakage(sub.price, li.unit_price, li.quantity or 1, sub.billing_interval)
        if monthly <= 0:
            continue

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Invoice price differs from subscription",
                severity="medium",
                confidence=CONFIDENCE_HIGH,
                customer_id=str(invoice.customer_id),
                subscription_id=str(sub.id),
                invoice_id=str(invoice.id),
                expected_value=sub.price,
                actual_value=li.unit_price,
                delta=sub.price - li.unit_price,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Align invoice line item pricing with subscription record.",
                evidence=[
                    EvidenceRecord(
                        field="unit_price",
                        expected=str(sub.price),
                        actual=str(li.unit_price),
                        reference_ids={"invoice": invoice.invoice_number},
                    )
                ],
            )
        )

    return findings
