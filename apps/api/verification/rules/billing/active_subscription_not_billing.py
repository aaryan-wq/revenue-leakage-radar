from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="active_subscription_not_billing",
        name="Active Subscription Not Billing",
        category="billing",
        purpose="Detect active subscriptions with no recent invoices.",
        trigger_description="subscription active but no invoice in expected billing window",
        ignored_cases="Recently created subscriptions.",
        severity_default="medium",
        leak_family="usage_monetization",
        recommendation_template="Investigate why active subscription is not generating invoices.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "status")
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.INVOICE, "invoice_date", optional=True)
    return spec


class ActiveSubscriptionNotBillingRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status):
                continue
            invoices = ctx.invoices_for_subscription(sub.id)
            if invoices:
                continue
            catalog = ctx.catalog_for_product(sub.product_id)
            expected_price = sub.price if sub.price and sub.price > 0 else (
                catalog.list_price if catalog and catalog.list_price else None
            )
            if expected_price is None:
                continue

            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                expected_price,
                Decimal("0"),
                sub.quantity or 1,
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub),
                    expected=expected_price,
                    actual=Decimal("0"),
                    difference=expected_price,
                    calculation=trace,
                    confidence=CONFIDENCE_MEDIUM,
                    severity="medium",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="invoice_count",
                            expected=">=1",
                            actual="0",
                        )
                    ],
                )
            )
        return findings


rule = ActiveSubscriptionNotBillingRule()
