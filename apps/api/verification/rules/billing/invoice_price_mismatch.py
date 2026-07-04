from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_line_item
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="invoice_price_mismatch",
        name="Invoice Price Mismatch",
        category="billing",
        purpose="Detect invoice line unit prices that differ from subscription price.",
        trigger_description="line_item.unit_price != subscription.price",
        ignored_cases="Missing subscription link.",
        severity_default="medium",
        leak_family="invoice_execution",
        recommendation_template="Align invoice line item with subscription price.",
    )
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "unit_price")
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "subscription_id")
    return spec


class InvoicePriceMismatchRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for line_item in ctx.line_items:
            if line_item.unit_price is None or not line_item.subscription_id:
                continue
            sub = ctx.subscription_by_id(line_item.subscription_id)
            if not sub or sub.price is None or line_item.unit_price == sub.price:
                continue
            invoice = ctx.invoice_by_id(line_item.invoice_id)
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                sub.price,
                line_item.unit_price,
                line_item.quantity or 1,
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
                            field="subscription_price",
                            expected=str(sub.price),
                            actual=str(line_item.unit_price),
                            reference_ids={"subscription_id": sub.external_subscription_id or str(sub.id)},
                        )
                    ],
                )
            )
        return findings


rule = InvoicePriceMismatchRule()
