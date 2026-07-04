from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="renewal_price_drift",
        name="Renewal Price Drift",
        category="pricing",
        purpose="Detect renewal invoices priced below prior period or contract expectation.",
        trigger_description="latest invoice unit/total < prior period expected price",
        ignored_cases="First invoice; missing invoice history.",
        severity_default="medium",
        leak_family="renewal_event",
        recommendation_template="Review renewal pricing against prior period and contract terms.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "subscription_id")
    spec.field(CanonicalEntity.INVOICE, "total")
    spec.field(CanonicalEntity.INVOICE, "invoice_date")
    spec.field(CanonicalEntity.INVOICE_LINE_ITEM, "unit_price", optional=True)
    spec.field(CanonicalEntity.CONTRACT, "expected_renewal_price", optional=True)
    return spec


class RenewalPriceDriftRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status):
                continue
            invoices = sorted(
                ctx.invoices_for_subscription(sub.id),
                key=lambda inv: inv.invoice_date or inv.id,
            )
            if len(invoices) < 2:
                continue
            prior, latest = invoices[-2], invoices[-1]
            qty = sub.quantity or 1

            prior_lines = ctx.line_items_for_invoice(prior.id)
            latest_lines = ctx.line_items_for_invoice(latest.id)
            if prior_lines and latest_lines and prior_lines[0].unit_price and latest_lines[0].unit_price:
                expected = prior_lines[0].unit_price
                actual = latest_lines[0].unit_price
                if actual >= expected:
                    continue
                difference = expected - actual
                monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                    expected,
                    actual,
                    qty,
                    sub.billing_interval,
                )
            elif prior.total is not None and latest.total is not None:
                expected = prior.total
                actual = latest.total
                contracts = ctx.contracts_for_customer(sub.customer_id)
                for contract in contracts:
                    if contract.expected_renewal_price is not None:
                        expected = max(expected, contract.expected_renewal_price)
                if actual >= expected:
                    continue
                difference = expected - actual
                monthly, annual, trace = FinancialCalculator.compute_period_leakage(
                    expected,
                    actual,
                    sub.billing_interval,
                )
            else:
                continue

            findings.append(
                make_result(
                    scope=scope_from_subscription(sub, latest),
                    expected=expected,
                    actual=actual,
                    difference=difference,
                    calculation=trace,
                    severity="medium",
                    confidence=CONFIDENCE_MEDIUM,
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="renewal_price",
                            expected=str(expected),
                            actual=str(actual),
                            reference_ids={
                                "prior_invoice": prior.external_invoice_id or str(prior.id),
                                "latest_invoice": latest.external_invoice_id or str(latest.id),
                            },
                        )
                    ],
                )
            )
        return findings


rule = RenewalPriceDriftRule()
