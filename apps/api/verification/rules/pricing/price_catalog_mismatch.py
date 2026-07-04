from __future__ import annotations

from datetime import timezone
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_line_item
from verification.rules.common import should_skip_discounted_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="price_catalog_mismatch",
        name="Price Catalog Mismatch",
        category="pricing",
        purpose="Detect invoice line prices below the active catalog list price.",
        trigger_description="line_item.unit_price < catalog.list_price for matching product and effective date",
        ignored_cases="Discounted subscriptions; missing catalog entry.",
        severity_default="high",
        leak_family="subscription_pricing_gap",
        recommendation_template="Reconcile line item unit price with active price catalog entry.",
    )
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "unit_price")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "product_id")
    spec.field(CanonicalEntity.PRICE, "list_price")
    spec.field(CanonicalEntity.PRICE, "effective_date")
    spec.field(CanonicalEntity.SUBSCRIPTION, "subscription_id", optional=True)
    spec.field(CanonicalEntity.INVOICE, "invoice_id", optional=True)
    return spec


class PriceCatalogMismatchRule:
    spec = _spec()

    def _evaluate_pair(self, ctx: CanonicalContext, line_item, invoice, as_of, sub) -> RuleResult | None:
        if line_item.unit_price is None or not line_item.product_id:
            return None
        if should_skip_discounted_subscription(sub, invoice):
            return None
        catalog = ctx.catalog_for_product(line_item.product_id, line_item.sku, as_of)
        if not catalog or catalog.list_price is None or line_item.unit_price >= catalog.list_price:
            return None
        interval = line_item.billing_interval or (catalog.billing_interval if catalog else None)
        if sub:
            interval = interval or sub.billing_interval
        interval = interval or "monthly"
        monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
            catalog.list_price,
            line_item.unit_price,
            line_item.quantity or 1,
            interval,
        )
        return make_result(
            scope=scope_from_line_item(line_item, invoice, sub),
            expected=catalog.list_price,
            actual=line_item.unit_price,
            difference=catalog.list_price - line_item.unit_price,
            calculation=trace,
            recommendation=self.spec.recommendation_template,
            evidence=[
                EvidenceInput(
                    field="unit_price",
                    expected=str(catalog.list_price),
                    actual=str(line_item.unit_price),
                    reference_ids={
                        "product_id": line_item.product_id or "",
                        "sku": line_item.sku or "",
                    },
                )
            ],
        )

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for line_item in ctx.line_items:
            invoice = ctx.invoice_by_id(line_item.invoice_id) if line_item.invoice_id else None
            subscription_id = line_item.subscription_id or (invoice.subscription_id if invoice else None)
            sub = ctx.subscription_by_id(subscription_id) if subscription_id else None
            as_of = line_item.line_item_date
            if as_of is None and invoice and invoice.invoice_date:
                as_of = invoice.invoice_date
            if as_of is None:
                as_of = ctx.reference_date
            if as_of.tzinfo is None:
                as_of = as_of.replace(tzinfo=timezone.utc)
            result = self._evaluate_pair(ctx, line_item, invoice, as_of, sub)
            if result:
                findings.append(result)
        return findings


rule = PriceCatalogMismatchRule()
