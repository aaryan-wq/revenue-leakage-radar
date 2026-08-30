from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_line_item
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="usage_billing_drift",
        name="Usage Billing Drift",
        category="billing",
        purpose="Detect invoiced usage amounts that diverge from rated subscription usage pricing.",
        trigger_description="invoice line usage charges diverge from subscription usage rate",
        ignored_cases="Non-usage subscriptions or missing line items.",
        severity_default="medium",
        leak_family="usage_monetization",
        recommendation_template="Reconcile usage-rated invoice lines against subscription pricing.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.SUBSCRIPTION, "quantity")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "unit_price")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "quantity")
    return spec


class UsageBillingDriftRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        tolerance = Decimal("0.05")
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.price:
                continue
            latest = ctx.latest_line_item_for_subscription(sub.id)
            if not latest:
                continue
            line_item, invoice, _ = latest
            if line_item.unit_price is None:
                continue
            expected_unit = Decimal(str(sub.price))
            actual_unit = Decimal(str(line_item.unit_price))
            if expected_unit <= 0:
                continue
            delta_pct = abs(actual_unit - expected_unit) / expected_unit
            if delta_pct <= tolerance:
                continue
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                sub.price,
                line_item.unit_price,
                line_item.quantity or sub.quantity or 1,
                line_item.billing_interval or sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_line_item(line_item, invoice, sub),
                    expected=sub.price,
                    actual=line_item.unit_price,
                    difference=abs(sub.price - line_item.unit_price),
                    calculation=trace,
                    severity="medium",
                    confidence=CONFIDENCE_MEDIUM,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="unit_price",
                            expected=str(expected_unit),
                            actual=str(actual_unit),
                            reference_ids={"subscription_id": sub.external_subscription_id or str(sub.id)},
                        )
                    ],
                )
            )
        return findings


rule = UsageBillingDriftRule()
