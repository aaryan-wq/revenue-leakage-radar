from __future__ import annotations

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="missing_expected_invoice",
        name="Missing Expected Invoice",
        category="billing",
        purpose="Detect gaps in expected recurring invoice schedule for active subscriptions.",
        trigger_description="active subscription missing invoice in expected billing period",
        ignored_cases="New subscriptions; trialing.",
        severity_default="medium",
        leak_family="invoice_execution",
        recommendation_template="Generate missing invoice for billing period.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "status")
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    spec.field(CanonicalEntity.INVOICE, "invoice_date")
    return spec


class MissingExpectedInvoiceRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        now = ctx.reference_date
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or sub.price is None:
                continue
            if (sub.status or "").lower() == "trialing":
                continue
            invoices = ctx.invoices_for_subscription(sub.id)
            if len(invoices) < 1:
                continue
            sorted_invoices = sorted(invoices, key=lambda inv: inv.invoice_date or inv.id)
            last = sorted_invoices[-1]
            if not last.invoice_date or not last.period_end:
                continue
            period_end = last.period_end
            if period_end.tzinfo is None:
                period_end = period_end.replace(tzinfo=timezone.utc)
            if period_end >= now - timedelta(days=7):
                continue
            monthly, annual, trace = FinancialCalculator.compute_recurring_leakage(
                sub.price,
                Decimal("0"),
                sub.quantity or 1,
                sub.billing_interval,
            )
            findings.append(
                make_result(
                    scope=scope_from_subscription(sub, last),
                    expected=sub.price,
                    actual=Decimal("0"),
                    difference=sub.price,
                    calculation=trace,
                    confidence=CONFIDENCE_MEDIUM,
                    severity="medium",
                    recommendation=self.spec.recommendation_template,
                    evidence=[
                        EvidenceInput(
                            field="expected_invoice_after",
                            expected=str(period_end.date()),
                            actual="missing",
                        )
                    ],
                )
            )
        return findings


rule = MissingExpectedInvoiceRule()
