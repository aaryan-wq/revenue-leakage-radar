from __future__ import annotations

from datetime import timezone
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult

GRANDFATHERED_MIN_AGE_DAYS = 365


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="grandfathered_pricing",
        name="Grandfathered Pricing",
        category="pricing",
        purpose="Detect legacy subscription pricing without an approved contract exception.",
        trigger_description="subscription.price < catalog.list_price and no matching contract",
        ignored_cases="Subscriptions with contract price exception; young subscriptions without CRM.",
        severity_default="medium",
        leak_family="subscription_pricing_gap",
        recommendation_template="Validate whether legacy pricing is contractually approved.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.SUBSCRIPTION, "product_id")
    spec.field(CanonicalEntity.SUBSCRIPTION, "start_date")
    spec.field(CanonicalEntity.PRICE, "list_price")
    spec.field(CanonicalEntity.CONTRACT, "contract_price", optional=True)
    return spec


class GrandfatheredPricingRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        ref = ctx.reference_date

        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.price or not sub.product_id or not sub.start_date:
                continue

            catalog = ctx.latest_catalog_version(sub.product_id)
            if not catalog or catalog.list_price is None or sub.price >= catalog.list_price:
                continue

            contracts = ctx.contracts_for_customer(sub.customer_id)
            if ctx.has_crm and contracts:
                has_exception = any(
                    contract.contract_price is not None and contract.contract_price < catalog.list_price
                    for contract in contracts
                )
                if has_exception:
                    continue

            start = sub.start_date
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            age_days = (ref - start).days
            if age_days < GRANDFATHERED_MIN_AGE_DAYS and not ctx.has_crm:
                continue

            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                catalog.list_price,
                sub.price,
                sub.quantity or 1,
                sub.billing_interval,
            )
            confidence = CONFIDENCE_HIGH if ctx.has_crm else CONFIDENCE_MEDIUM
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub),
                    expected=catalog.list_price,
                    actual=sub.price,
                    difference=catalog.list_price - sub.price,
                    calculation=trace,
                    confidence=confidence,
                    severity="medium",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="grandfathered_price",
                            expected=str(catalog.list_price),
                            actual=str(sub.price),
                            reference_ids={"product_id": sub.product_id or ""},
                        )
                    ],
                )
            )
        return findings


rule = GrandfatheredPricingRule()
