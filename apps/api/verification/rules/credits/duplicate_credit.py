from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope


def _has_credit_data(ctx: CanonicalContext) -> tuple[bool, str | None]:
    if not ctx.has_credit_data:
        return False, "Credit amount data not present in invoices"
    return True, None


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="duplicate_credit",
        name="Duplicate Credit",
        category="credits",
        purpose="Detect duplicate credit amounts applied to the same invoice or customer.",
        trigger_description="same credit amount repeated for customer within billing period",
        ignored_cases="Single credit per invoice.",
        severity_default="high",
        leak_family="operational",
        recommendation_template="Remove duplicate credit application.",
        eligibility_conditions=_has_credit_data,
    )
    spec.field(CanonicalEntity.INVOICE, "credit_amount")
    spec.field(CanonicalEntity.INVOICE, "customer_id")
    return spec


class DuplicateCreditRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        by_customer_amount: dict[tuple[str, str], list] = defaultdict(list)
        for invoice in ctx.invoices:
            if not invoice.credit_amount or invoice.credit_amount <= 0 or not invoice.customer_id:
                continue
            key = (str(invoice.customer_id), str(invoice.credit_amount))
            by_customer_amount[key].append(invoice)

        for (customer_id, amount_str), invoices in by_customer_amount.items():
            if len(invoices) < 2:
                continue
            amount = Decimal(amount_str)
            monthly, annual, trace = FinancialCalculator.compute_period_leakage(amount, Decimal("0"), "monthly")
            findings.append(
                make_result(
                    scope=RuleScope(customer_id=customer_id, invoice_id=str(invoices[-1].id)),
                    expected=amount,
                    actual=amount * Decimal(len(invoices) - 1),
                    difference=amount * Decimal(len(invoices) - 1),
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="duplicate_credit",
                            expected="1",
                            actual=str(len(invoices)),
                            reference_ids={"credit_amount": amount_str},
                        )
                    ],
                )
            )
        return findings


rule = DuplicateCreditRule()
