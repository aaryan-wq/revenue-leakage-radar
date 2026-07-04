from __future__ import annotations

from collections import defaultdict
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result
from verification.types import EvidenceInput, RuleResult, RuleScope


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="duplicate_discount",
        name="Duplicate Discount",
        category="discounts",
        purpose="Detect the same coupon code applied multiple times to one subscription.",
        trigger_description="same coupon appears on multiple invoices for one subscription",
        ignored_cases="Single coupon application.",
        severity_default="high",
        leak_family="discount_integrity",
        recommendation_template="Remove duplicate coupon applications.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "coupon_id")
    spec.field(CanonicalEntity.INVOICE, "discount")
    spec.field(CanonicalEntity.COUPON, "code")
    return spec


class DuplicateDiscountRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        discounted_invoices_by_sub: dict[str, list] = defaultdict(list)
        for invoice in ctx.invoices:
            if invoice.subscription_id and invoice.discount and invoice.discount > 0:
                discounted_invoices_by_sub[str(invoice.subscription_id)].append(invoice)

        for sub in ctx.subscriptions:
            if not sub.coupon_id:
                continue
            invoices = discounted_invoices_by_sub.get(str(sub.id), [])
            if len(invoices) < 2:
                continue
            duplicate_amount = sum(invoice.discount or Decimal("0") for invoice in invoices[1:])
            if duplicate_amount <= 0:
                continue
            monthly, annual, trace = FinancialCalculator.compute_period_leakage(
                Decimal("0"),
                duplicate_amount,
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=RuleScope(
                        customer_id=str(sub.customer_id),
                        subscription_id=str(sub.id),
                        invoice_id=str(invoices[-1].id),
                    ),
                    expected=Decimal("0"),
                    actual=duplicate_amount,
                    difference=duplicate_amount,
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="duplicate_coupon",
                            expected="1 application",
                            actual=f"{len(invoices)} invoices with discount",
                            reference_ids={"coupon": sub.coupon_id or ""},
                        )
                    ],
                )
            )
        return findings


rule = DuplicateDiscountRule()
