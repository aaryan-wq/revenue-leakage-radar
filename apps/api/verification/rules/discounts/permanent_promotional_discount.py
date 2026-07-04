from __future__ import annotations

from datetime import timezone
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
        rule_id="permanent_promotional_discount",
        name="Permanent Promotional Discount",
        category="discounts",
        purpose="Detect promotional coupons still active beyond contract end date.",
        trigger_description="coupon active and contract.end_date passed",
        ignored_cases="No contract; non-promotional coupons.",
        severity_default="high",
        leak_family="discount_integrity",
        recommendation_template="End promotional discount after contract terms expire.",
        eligibility_conditions=_has_contract_data,
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "coupon_id")
    spec.field(CanonicalEntity.CONTRACT, "end_date")
    return spec


class PermanentPromotionalDiscountRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        now = ctx.reference_date
        for sub in ctx.subscriptions:
            if not sub.coupon_id or not is_active_subscription(sub.status):
                continue
            contracts = ctx.contracts_for_customer(sub.customer_id)
            ended_contracts = []
            for contract in contracts:
                if not contract.end_date:
                    continue
                end = contract.end_date
                if end.tzinfo is None:
                    end = end.replace(tzinfo=timezone.utc)
                if end < now:
                    ended_contracts.append(contract)
            if not ended_contracts:
                continue
            trace = FinancialCalculator.compute_zero_leakage(semantics="operational")
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub),
                    expected=Decimal("0"),
                    actual=Decimal("0"),
                    difference=Decimal("0"),
                    calculation=trace,
                    severity="high",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="contract_end_date",
                            expected="discount ended",
                            actual=str(ended_contracts[0].end_date.date()),
                            reference_ids={"coupon": sub.coupon_id or ""},
                        )
                    ],
                )
            )
        return findings


rule = PermanentPromotionalDiscountRule()
