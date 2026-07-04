from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_line_item
from verification.types import EvidenceInput, RuleResult


def _has_manual_override(ctx: CanonicalContext) -> tuple[bool, str | None]:
    if not ctx.has_manual_override_data:
        return False, "Manual override flags not present in line items"
    return True, None


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="manual_price_override",
        name="Manual Price Override",
        category="pricing",
        purpose="Detect manually overridden line item prices below catalog.",
        trigger_description="line_item.is_manual_override and unit_price < catalog.list_price",
        ignored_cases="Non-override line items.",
        severity_default="high",
        leak_family="invoice_execution",
        recommendation_template="Review manual override and align with approved pricing.",
        eligibility_conditions=_has_manual_override,
    )
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "is_manual_override")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "unit_price")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "product_id")
    spec.field(CanonicalEntity.PRICE, "list_price")
    return spec


class ManualPriceOverrideRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for line_item in ctx.line_items:
            if not line_item.is_manual_override or line_item.unit_price is None or not line_item.product_id:
                continue
            invoice = ctx.invoice_by_id(line_item.invoice_id)
            sub = ctx.subscription_by_id(line_item.subscription_id) if line_item.subscription_id else None
            as_of = invoice.invoice_date if invoice and invoice.invoice_date else None
            catalog = ctx.catalog_for_product(line_item.product_id, line_item.sku, as_of=as_of)
            if not catalog or catalog.list_price is None or line_item.unit_price >= catalog.list_price:
                continue
            interval = line_item.billing_interval or (sub.billing_interval if sub else None) or catalog.billing_interval
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                catalog.list_price,
                line_item.unit_price,
                line_item.quantity or 1,
                interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_line_item(line_item, invoice, sub),
                    expected=catalog.list_price,
                    actual=line_item.unit_price,
                    difference=catalog.list_price - line_item.unit_price,
                    calculation=trace,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="manual_override",
                            expected="false",
                            actual="true",
                            reference_ids={"line_item_id": line_item.external_line_item_id or str(line_item.id)},
                        )
                    ],
                )
            )
        return findings


rule = ManualPriceOverrideRule()
