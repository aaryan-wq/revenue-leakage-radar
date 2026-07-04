from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_line_item
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="incorrect_addon_price",
        name="Incorrect Add-on Price",
        category="pricing",
        purpose="Detect add-on product line items priced below latest catalog version.",
        trigger_description="line_item.unit_price < latest catalog.list_price for add-on SKU",
        ignored_cases="Primary subscription lines; matching catalog price.",
        severity_default="high",
        leak_family="subscription_pricing_gap",
        recommendation_template="Update add-on line item to latest catalog price.",
    )
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "unit_price")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "product_id")
    spec.field(CanonicalEntity.PRICE, "list_price")
    spec.field(CanonicalEntity.PRICE, "effective_date")
    return spec


class IncorrectAddonPriceRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for line_item in ctx.line_items:
            if not line_item.product_id or line_item.unit_price is None:
                continue
            sub = ctx.subscription_by_id(line_item.subscription_id) if line_item.subscription_id else None
            if sub and line_item.product_id == sub.product_id:
                continue
            latest = ctx.latest_catalog_version(line_item.product_id, line_item.sku)
            if not latest or latest.list_price is None or line_item.unit_price >= latest.list_price:
                continue
            invoice = ctx.invoice_by_id(line_item.invoice_id)
            interval = line_item.billing_interval or (latest.billing_interval if latest else None)
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                latest.list_price,
                line_item.unit_price,
                line_item.quantity or 1,
                interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_line_item(line_item, invoice, sub),
                    expected=latest.list_price,
                    actual=line_item.unit_price,
                    difference=latest.list_price - line_item.unit_price,
                    calculation=trace,
                    severity="medium",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="addon_unit_price",
                            expected=str(latest.list_price),
                            actual=str(line_item.unit_price),
                            reference_ids={"product_id": line_item.product_id},
                        )
                    ],
                )
            )
        return findings


rule = IncorrectAddonPriceRule()
