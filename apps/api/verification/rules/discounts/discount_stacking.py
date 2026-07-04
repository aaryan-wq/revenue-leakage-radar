from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope

STACKED_DISCOUNT_CAP_RATIO = Decimal("0.1")


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="discount_stacking",
        name="Discount Stacking",
        category="discounts",
        purpose="Detect multiple discounts compounding on the same invoice.",
        trigger_description="invoice has subscription coupon and invoice-level discount",
        ignored_cases="Single discount source.",
        severity_default="high",
        leak_family="discount_integrity",
        recommendation_template="Remove duplicate discount application.",
    )
    spec.field(CanonicalEntity.INVOICE, "discount")
    spec.field(CanonicalEntity.SUBSCRIPTION, "coupon_id")
    spec.field(CanonicalEntity.INVOICE, "subscription_id")
    return spec


class DiscountStackingRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for invoice in ctx.invoices:
            if not invoice.discount or invoice.discount <= 0 or not invoice.subscription_id:
                continue
            sub = ctx.subscription_by_id(invoice.subscription_id)
            if not sub or not sub.coupon_id:
                continue
            coupon = ctx.coupon_by_code(sub.coupon_id)
            if not coupon:
                continue
            base = invoice.subtotal or invoice.total or Decimal("0")
            if base <= 0:
                continue
            stacked_loss = min(invoice.discount, base * STACKED_DISCOUNT_CAP_RATIO)
            monthly, annual, trace = FinancialCalculator.compute_period_leakage(
                stacked_loss,
                Decimal("0"),
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=RuleScope(
                        customer_id=str(invoice.customer_id),
                        subscription_id=str(sub.id),
                        invoice_id=str(invoice.id),
                    ),
                    expected=base,
                    actual=base - invoice.discount,
                    difference=invoice.discount,
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="stacked_discount",
                            expected="single discount",
                            actual=f"coupon + invoice discount {invoice.discount}",
                            reference_ids={"invoice": invoice.external_invoice_id or str(invoice.id)},
                        )
                    ],
                )
            )
        return findings


rule = DiscountStackingRule()
