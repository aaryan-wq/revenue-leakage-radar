from __future__ import annotations

from decimal import Decimal

from core.canonical_entities import CanonicalEntity
from verification.calculator.financial import CONFIDENCE_HIGH, FinancialCalculator
from verification.context import CanonicalContext
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult

CANCELLED_STATUSES = frozenset({"canceled", "cancelled", "inactive", "ended"})


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="cancelled_subscription_still_billing",
        name="Cancelled Subscription Still Billing",
        category="billing",
        purpose="Detect invoices issued after subscription cancellation.",
        trigger_description="subscription cancelled but invoice issued after cancellation",
        ignored_cases="Active subscriptions.",
        severity_default="high",
        leak_family="invoice_execution",
        recommendation_template="Stop billing cancelled subscriptions and review erroneous invoices.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "status")
    spec.field(CanonicalEntity.INVOICE, "invoice_date")
    spec.field(CanonicalEntity.INVOICE, "total")
    return spec


class CancelledSubscriptionStillBillingRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if (sub.status or "").lower() not in CANCELLED_STATUSES:
                continue
            cancel_date = sub.renewal_date or sub.start_date
            for invoice in ctx.invoices_for_subscription(sub.id):
                if not invoice.invoice_date or invoice.total is None:
                    continue
                if cancel_date and invoice.invoice_date > cancel_date:
                    monthly, annual, trace = FinancialCalculator.compute_period_leakage(
                        Decimal("0"),
                        invoice.total,
                        sub.billing_interval,
                    )
                    findings.append(
                        make_result(
                            scope=scope_from_subscription(sub, invoice),
                            expected=Decimal("0"),
                            actual=invoice.total,
                            difference=invoice.total,
                            calculation=trace,
                            recommendation=self.spec.recommendation_template,
                            evidence=[
                                EvidenceInput(
                                    field="post_cancel_invoice",
                                    expected="no billing after cancel",
                                    actual=str(invoice.invoice_date.date()),
                                    reference_ids={"invoice": invoice.external_invoice_id or str(invoice.id)},
                                )
                            ],
                        )
                    )
                    break
        return findings


rule = CancelledSubscriptionStillBillingRule()
