from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="discount_wrong_product",
        name="Discount Applied to Wrong Product",
        category="discounts",
        purpose="Detect coupon applied to subscription product that does not match coupon scope.",
        trigger_description="subscription has coupon but catalog product mismatch on discounted invoice line",
        ignored_cases="Matching product lines.",
        severity_default="high",
        leak_family="discount_integrity",
        recommendation_template="Apply coupon only to eligible products.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "coupon_id")
    spec.field(CanonicalEntity.SUBSCRIPTION, "product_id")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "product_id")
    spec.field(CanonicalEntity.INVOICE, "discount")
    return spec


class DiscountWrongProductRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not sub.coupon_id or not is_active_subscription(sub.status) or not sub.product_id:
                continue
            for invoice in ctx.invoices_for_subscription(sub.id):
                if not invoice.discount or invoice.discount <= 0:
                    continue
                for line_item in ctx.line_items_for_invoice(invoice.id):
                    if not line_item.product_id or line_item.product_id == sub.product_id:
                        continue
                    if line_item.unit_price is None:
                        continue
                    catalog = ctx.catalog_for_product(line_item.product_id, line_item.sku)
                    if not catalog or catalog.list_price is None:
                        continue
                    monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                        catalog.list_price,
                        line_item.unit_price,
                        line_item.quantity or 1,
                        line_item.billing_interval or sub.billing_interval,
                    )
                    findings.append(
                        make_result(
                            scope=scope_from_subscription(sub, invoice, line_item.product_id),
                            expected=catalog.list_price,
                            actual=line_item.unit_price,
                            difference=catalog.list_price - line_item.unit_price,
                            calculation=trace,
                            recommendation=self.spec.recommendation_template,
                            evidence=[
                                EvidenceInput(
                                    field="wrong_product_discount",
                                    expected=sub.product_id,
                                    actual=line_item.product_id,
                                    reference_ids={"coupon": sub.coupon_id or ""},
                                )
                            ],
                        )
                    )
                    break
        return findings


rule = DiscountWrongProductRule()
