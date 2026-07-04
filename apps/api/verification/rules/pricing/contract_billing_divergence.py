from __future__ import annotations

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="contract_billing_price_divergence",
        name="Contract vs Billing Price Divergence",
        category="pricing",
        purpose="Detect subscription billing prices that diverge from contracted unit price.",
        trigger_description="subscription.price != contract.contract_price for CRM customer",
        ignored_cases="Matching contract and subscription prices; missing contract price.",
        severity_default="high",
        leak_family="subscription_pricing_gap",
        recommendation_template="Align subscription price with contracted unit price.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.CONTRACT, "contract_price")
    spec.field(CanonicalEntity.CONTRACT, "customer_id")
    return spec


class ContractBillingDivergenceRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        if not ctx.has_crm:
            return []

        findings: list[RuleResult] = []
        for contract in ctx.crm_contracts:
            if not contract.contract_price or not contract.customer_id:
                continue

            for sub in ctx.subscriptions_for_customer(contract.customer_id):
                if not sub.price or sub.price == contract.contract_price:
                    continue

                monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                    contract.contract_price,
                    sub.price,
                    sub.quantity or 1,
                    sub.billing_interval,
                )
                findings.append(
                    make_result(
                        scope=scope_from_subscription(sub),
                        expected=contract.contract_price,
                        actual=sub.price,
                        difference=abs(contract.contract_price - sub.price),
                        calculation=trace,
                        recommendation=self.spec.recommendation_template,
                        evidence=[
                            EvidenceInput(
                                field="contract_price",
                                expected=str(contract.contract_price),
                                actual=str(sub.price),
                                reference_ids={
                                    "contract": contract.external_contract_id or "",
                                },
                            )
                        ],
                    )
                )
        return findings


rule = ContractBillingDivergenceRule()
