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
        rule_id="incorrect_seat_price",
        name="Incorrect Seat Price",
        category="pricing",
        purpose="Detect unbilled seats when CRM seat count exceeds billed subscription quantity.",
        trigger_description="CRM seat_count > subscription.quantity billed at subscription unit price",
        ignored_cases="Matching seat counts.",
        severity_default="high",
        leak_family="usage_monetization",
        recommendation_template="Bill for all active seats at the subscription unit price.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.SUBSCRIPTION, "quantity")
    spec.field(CanonicalEntity.ACCOUNT, "seat_count")
    return spec


class IncorrectSeatPriceRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.price:
                continue
            account = ctx.crm_account_for_customer(sub.customer_id)
            if not account or not account.seat_count:
                continue
            billed_seats = sub.quantity or 1
            if account.seat_count <= billed_seats:
                continue
            monthly, annual, trace = FinancialCalculator.seat_delta(
                account.seat_count,
                billed_seats,
                sub.price,
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub),
                    expected=Decimal(str(account.seat_count)),
                    actual=Decimal(str(billed_seats)),
                    difference=Decimal(str(account.seat_count - billed_seats)),
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="seat_count",
                            expected=str(account.seat_count),
                            actual=str(billed_seats),
                            reference_ids={"account_id": account.external_account_id or str(account.id)},
                        )
                    ],
                )
            )
        return findings


rule = IncorrectSeatPriceRule()
