from datetime import timezone
from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "expired_discount_still_applied"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for sub in ctx.subscriptions:
        if not sub.coupon_id or (sub.status and sub.status.lower() not in ("active", "trialing")):
            continue

        coupon = ctx.coupon_by_code(sub.coupon_id)
        if not coupon or not coupon.expires_at:
            continue

        sub_invoices = ctx.invoices_for_subscription(sub.id)
        for invoice in sub_invoices:
            if not invoice.invoice_date or not invoice.discount:
                continue
            if invoice.discount <= 0:
                continue

            inv_date = invoice.invoice_date
            if inv_date.tzinfo is None:
                inv_date = inv_date.replace(tzinfo=timezone.utc)
            exp = coupon.expires_at
            if exp.tzinfo is None:
                exp = exp.replace(tzinfo=timezone.utc)

            if exp >= inv_date:
                continue

            catalog = ctx.catalog_for_product(sub.product_id, as_of=inv_date)
            if not catalog or not catalog.list_price or not sub.price:
                continue

            monthly, annual = compute_leakage(
                catalog.list_price, sub.price, sub.quantity or 1, sub.billing_interval
            )
            if monthly <= 0:
                continue

            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Expired discount still applied",
                    severity="high",
                    confidence=CONFIDENCE_HIGH,
                    customer_id=str(sub.customer_id),
                    subscription_id=str(sub.id),
                    invoice_id=str(invoice.id),
                    expected_value=catalog.list_price,
                    actual_value=sub.price,
                    delta=catalog.list_price - sub.price,
                    estimated_monthly_loss=monthly,
                    estimated_arr_loss=annual,
                    recommendation="Remove expired coupon and reprice subscription to current catalog rate.",
                    evidence=[
                        EvidenceRecord(
                            field="coupon_expires_at",
                            expected=str(exp.date()),
                            actual=str(inv_date.date()),
                            reference_ids={"coupon": coupon.code, "invoice": invoice.invoice_number},
                        )
                    ],
                )
            )

    return findings
