from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="currency_mismatch",
        name="Currency Mismatch",
        category="data_quality",
        purpose="Detect currency inconsistencies across subscription, invoice, and catalog.",
        trigger_description="invoice.currency != subscription.currency OR price_catalog.currency",
        ignored_cases="Consistent currencies.",
        severity_default="high",
        leak_family="operational",
        recommendation_template="Align currency across billing records.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "currency")
    spec.field(CanonicalEntity.INVOICE, "currency")
    spec.field(CanonicalEntity.PRICE, "currency", optional=True)
    return spec


class CurrencyMismatchRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.currency:
                continue
            sub_currency = sub.currency.upper()
            for invoice in ctx.invoices_for_subscription(sub.id):
                if not invoice.currency:
                    continue
                if invoice.currency.upper() == sub_currency:
                    continue
                trace = FinancialCalculator.compute_zero_leakage(semantics="operational")
                findings.append(
                    make_result(
                        scope=scope_from_subscription(sub, invoice),
                        expected=Decimal("0"),
                        actual=Decimal("0"),
                        difference=Decimal("0"),
                        calculation=trace,
                        severity="high",
                        confidence=Decimal("90"),
                        recommendation=self.spec.recommendation_template,
                        evidence=[
                            EvidenceInput(
                                field="currency",
                                expected=sub_currency,
                                actual=invoice.currency.upper(),
                                reference_ids={"invoice": invoice.external_invoice_id or str(invoice.id)},
                            )
                        ],
                    )
                )
                break
            catalog = ctx.catalog_for_product(sub.product_id)
            if catalog and catalog.currency and catalog.currency.upper() != sub_currency:
                trace = FinancialCalculator.compute_zero_leakage(semantics="operational")
                findings.append(
                    make_result(
                        scope=scope_from_subscription(sub),
                        expected=Decimal("0"),
                        actual=Decimal("0"),
                        difference=Decimal("0"),
                        calculation=trace,
                        severity="high",
                        confidence=Decimal("90"),
                        recommendation=self.spec.recommendation_template,
                        evidence=[
                            EvidenceInput(
                                field="catalog_currency",
                                expected=sub_currency,
                                actual=catalog.currency.upper(),
                                reference_ids={"product_id": sub.product_id or ""},
                            )
                        ],
                    )
                )
        return findings


rule = CurrencyMismatchRule()
