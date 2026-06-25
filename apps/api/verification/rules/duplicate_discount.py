from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "duplicate_discount_stacking"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for invoice in ctx.invoices:
        if not invoice.discount or invoice.discount <= 0:
            continue
        if not invoice.subscription_id:
            continue

        sub = next((s for s in ctx.subscriptions if s.id == invoice.subscription_id), None)
        if not sub or not sub.coupon_id:
            continue

        coupon = ctx.coupon_by_code(sub.coupon_id)
        if not coupon:
            continue

        base = invoice.subtotal or invoice.total or Decimal("0")
        if base <= 0:
            continue

        stacked_loss = min(invoice.discount, base * Decimal("0.1"))
        monthly = (stacked_loss).quantize(Decimal("0.0001"))
        annual = (monthly * Decimal("12")).quantize(Decimal("0.0001"))

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Duplicate discount stacking detected",
                severity="high",
                confidence=CONFIDENCE_HIGH,
                customer_id=str(invoice.customer_id),
                subscription_id=str(sub.id),
                invoice_id=str(invoice.id),
                expected_value=base,
                actual_value=base - invoice.discount,
                delta=invoice.discount,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Review stacked coupon and invoice-level discounts for this subscription.",
                evidence=[
                    EvidenceRecord(
                        field="discount_stacking",
                        expected="single discount",
                        actual=f"coupon={sub.coupon_id}, invoice_discount={invoice.discount}",
                        reference_ids={"invoice": invoice.invoice_number},
                    )
                ],
            )
        )

    return findings
