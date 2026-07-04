from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="duplicate_customer",
        name="Duplicate Customer",
        category="data_quality",
        purpose="Detect duplicate customer records that may cause billing reconciliation issues.",
        trigger_description="multiple customers share same name or external id pattern",
        ignored_cases="Unique customers.",
        severity_default="low",
        leak_family="operational",
        recommendation_template="Merge duplicate customer records.",
    )
    spec.field(CanonicalEntity.CUSTOMER, "customer_id")
    return spec


class DuplicateCustomerRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        by_name: dict[str, list] = defaultdict(list)
        for customer in ctx.customers:
            if not customer.name:
                continue
            by_name[customer.name.strip().lower()].append(customer)

        for name, customers in by_name.items():
            if len(customers) < 2:
                continue
            trace = FinancialCalculator.compute_zero_leakage(semantics="operational")
            findings.append(
                make_result(
                    scope=RuleScope(customer_id=str(customers[0].id)),
                    expected=Decimal("1"),
                    actual=Decimal(str(len(customers))),
                    difference=Decimal(str(len(customers) - 1)),
                    calculation=trace,
                    severity="low",
                    confidence=Decimal("90"),
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="duplicate_customer_name",
                            expected="unique",
                            actual=name,
                            reference_ids={
                                "customer_ids": ",".join(
                                    customer.external_customer_id or str(customer.id) for customer in customers
                                )
                            },
                        )
                    ],
                )
            )
        return findings


rule = DuplicateCustomerRule()
