from __future__ import annotations

from datetime import timezone
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="expired_discount",
        name="Expired Discount",
        category="discounts",
        purpose="Detect discounts applied after coupon expiration date.",
        trigger_description="coupon.expires_at < invoice.invoice_date and discount applied",
        ignored_cases="Active coupons; subscriptions without coupons.",
        severity_default="high",
        leak_family="discount_integrity",
        recommendation_template="Remove expired coupon and reprice to catalog rate.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "coupon_id")
    spec.field(CanonicalEntity.COUPON, "expires_at")
    spec.field(CanonicalEntity.INVOICE, "discount")
    spec.field(CanonicalEntity.INVOICE, "invoice_date")
    spec.field(CanonicalEntity.PRICE, "list_price", optional=True)
    return spec


class ExpiredDiscountRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not sub.coupon_id or not is_active_subscription(sub.status):
                continue
            coupon = ctx.coupon_by_code(sub.coupon_id)
            if not coupon or not coupon.expires_at:
                continue
            expires = coupon.expires_at
            if expires.tzinfo is None:
                expires = expires.replace(tzinfo=timezone.utc)
            evidence_invoice = None
            for invoice in ctx.invoices_for_subscription(sub.id):
                if not invoice.invoice_date or not invoice.discount or invoice.discount <= 0:
                    continue
                inv_date = invoice.invoice_date
                if inv_date.tzinfo is None:
                    inv_date = inv_date.replace(tzinfo=timezone.utc)
                if expires >= inv_date:
                    continue
                evidence_invoice = invoice
                break
            if not evidence_invoice or not sub.price:
                continue
            catalog = ctx.catalog_for_product(sub.product_id, as_of=evidence_invoice.invoice_date)
            if not catalog or catalog.list_price is None or sub.price >= catalog.list_price:
                continue
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                catalog.list_price,
                sub.price,
                sub.quantity or 1,
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub, evidence_invoice),
                    expected=catalog.list_price,
                    actual=sub.price,
                    difference=catalog.list_price - sub.price,
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="coupon_expires_at",
                            expected=str(expires.date()),
                            actual=str(evidence_invoice.invoice_date.date()),
                            reference_ids={"coupon": coupon.code},
                        )
                    ],
                )
            )
        return findings


rule = ExpiredDiscountRule()
