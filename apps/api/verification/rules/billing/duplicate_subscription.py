from __future__ import annotations

from collections import defaultdict

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="duplicate_subscription",
        name="Duplicate Subscription",
        category="billing",
        purpose="Detect multiple active subscriptions for the same customer and product.",
        trigger_description="same customer_id + product_id has >1 active subscription",
        ignored_cases="Single active subscription per product.",
        severity_default="high",
        leak_family="usage_monetization",
        recommendation_template="Consolidate duplicate active subscriptions.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "customer_id")
    spec.field(CanonicalEntity.SUBSCRIPTION, "product_id")
    spec.field(CanonicalEntity.SUBSCRIPTION, "status")
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    return spec


class DuplicateSubscriptionRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        groups: dict[tuple[str, str], list] = defaultdict(list)
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.product_id:
                continue
            groups[(str(sub.customer_id), sub.product_id)].append(sub)

        for (customer_id, product_id), subs in groups.items():
            if len(subs) < 2:
                continue
            primary = subs[0]
            if primary.price is None:
                continue
            duplicate_count = len(subs) - 1
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                primary.price,
                __import__("decimal").Decimal("0"),
                duplicate_count,
                primary.billing_interval,
            )
            findings.append(
                make_result(
                    scope=RuleScope(
                        customer_id=customer_id,
                        subscription_id=str(subs[1].id),
                        product_id=product_id,
                    ),
                    expected=primary.price,
                    actual=__import__("decimal").Decimal("0"),
                    difference=primary.price,
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="duplicate_subscriptions",
                            expected="1",
                            actual=str(len(subs)),
                            reference_ids={"product_id": product_id},
                        )
                    ],
                )
            )
        return findings


rule = DuplicateSubscriptionRule()
