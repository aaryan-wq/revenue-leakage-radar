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
        rule_id="legacy_pricing",
        name="Legacy Pricing",
        category="pricing",
        purpose="Detect subscriptions priced below catalog after a newer price became effective.",
        trigger_description="subscription.price < catalog.list_price where catalog.effective_date > subscription.start_date",
        ignored_cases="Discounted subscriptions; missing catalog or start date.",
        severity_default="medium",
        leak_family="subscription_pricing_gap",
        recommendation_template="Reprice subscription to the active catalog rate.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.SUBSCRIPTION, "start_date")
    spec.field(CanonicalEntity.SUBSCRIPTION, "product_id")
    spec.field(CanonicalEntity.PRICE, "list_price")
    spec.field(CanonicalEntity.PRICE, "effective_date")
    spec.field(CanonicalEntity.INVOICE, "invoice_date", optional=True)
    return spec


class LegacyPricingRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.price or not sub.start_date or not sub.product_id:
                continue
            if sub.coupon_id:
                continue
            catalog = ctx.catalog_for_product(sub.product_id, as_of=sub.start_date)
            if not catalog or catalog.list_price is None or catalog.effective_date is None:
                continue
            if catalog.effective_date <= sub.start_date:
                continue
            if sub.price >= catalog.list_price:
                continue
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                catalog.list_price,
                sub.price,
                sub.quantity or 1,
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub),
                    expected=catalog.list_price,
                    actual=sub.price,
                    difference=catalog.list_price - sub.price,
                    calculation=trace,
                    severity="medium",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="catalog_effective_date",
                            expected=str(catalog.effective_date.date()),
                            actual=str(sub.start_date.date()),
                            reference_ids={"product_id": sub.product_id or ""},
                        )
                    ],
                )
            )
        return findings


rule = LegacyPricingRule()
