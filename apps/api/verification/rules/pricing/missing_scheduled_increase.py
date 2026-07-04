from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _has_contract_data(ctx: CanonicalContext) -> tuple[bool, str | None]:
    if not ctx.has_crm:
        return False, "CRM contract data not available"
    return True, None


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="missing_scheduled_increase",
        name="Missing Scheduled Increase",
        category="pricing",
        purpose="Detect contracts where scheduled price increase date passed without billing uplift.",
        trigger_description="contract.price_increase_date < today and subscription.price unchanged",
        ignored_cases="Contracts without increase date; already repriced subscriptions.",
        severity_default="high",
        leak_family="subscription_pricing_gap",
        recommendation_template="Apply scheduled contract price increase to subscription billing.",
        eligibility_conditions=_has_contract_data,
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.CONTRACT, "price_increase_date")
    spec.field(CanonicalEntity.CONTRACT, "contract_price")
    spec.field(CanonicalEntity.CONTRACT, "customer_id")
    return spec


class MissingScheduledIncreaseRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        now = ctx.reference_date
        for contract in ctx.crm_contracts:
            if not contract.price_increase_date or not contract.customer_id:
                continue
            increase_date = contract.price_increase_date
            if increase_date.tzinfo is None:
                increase_date = increase_date.replace(tzinfo=timezone.utc)
            if increase_date > now:
                continue
            expected_price = contract.expected_renewal_price or contract.contract_price
            if expected_price is None:
                continue
            for sub in ctx.subscriptions_for_customer(contract.customer_id):
                if not is_active_subscription(sub.status) or sub.price is None:
                    continue
                if sub.price >= expected_price:
                    continue
                monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                    expected_price,
                    sub.price,
                    sub.quantity or 1,
                    sub.billing_interval,
                )
                findings.append(
                    make_result(
                        scope=scope_from_subscription(sub),
                        expected=expected_price,
                        actual=sub.price,
                        difference=expected_price - sub.price,
                        calculation=trace,
                        recommendation=self.spec.recommendation_template,
                        evidence=[
                            EvidenceInput(
                                field="price_increase_date",
                                expected=str(increase_date.date()),
                                actual=str(now.date()),
                                reference_ids={"contract_id": contract.external_contract_id or ""},
                            )
                        ],
                    )
                )
        return findings


rule = MissingScheduledIncreaseRule()
