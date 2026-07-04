from __future__ import annotations

from verification.calculator.financial import CONFIDENCE_MEDIUM, FinancialCalculator, normalize_interval
from core.canonical_entities import CanonicalEntity
from verification.context import CanonicalContext, is_active_subscription
from verification.eligibility.schema import RuleSpec
from verification.rules.base import make_result, scope_from_subscription
from verification.types import EvidenceInput, RuleResult


def _spec() -> RuleSpec:
    spec = RuleSpec(
        rule_id="billing_frequency_mismatch",
        name="Billing Frequency Mismatch",
        category="billing",
        purpose="Detect invoices whose period does not match subscription billing interval.",
        trigger_description="subscription.billing_interval != invoice implied frequency",
        ignored_cases="Missing interval data.",
        severity_default="medium",
        leak_family="invoice_execution",
        recommendation_template="Align invoice billing frequency with subscription interval.",
    )
    spec.field(CanonicalEntity.SUBSCRIPTION, "billing_interval")
    spec.field(CanonicalEntity.INVOICE, "period_start")
    spec.field(CanonicalEntity.INVOICE, "period_end")
    spec.field(CanonicalEntity.SUBSCRIPTION, "price")
    return spec


EXPECTED_PERIOD_DAYS = {
    "monthly": 28,
    "month": 28,
    "quarterly": 88,
    "quarter": 88,
    "annual": 360,
    "yearly": 360,
    "year": 360,
}


class BillingFrequencyMismatchRule:
    spec = _spec()

    def evaluate(self, ctx: CanonicalContext) -> list[RuleResult]:
        findings: list[RuleResult] = []
        for sub in ctx.subscriptions:
            if not is_active_subscription(sub.status) or not sub.billing_interval:
                continue
            sub_interval = normalize_interval(sub.billing_interval)
            expected_days = EXPECTED_PERIOD_DAYS.get(sub_interval)
            if expected_days is None:
                continue
            for invoice in ctx.invoices_for_subscription(sub.id):
                if not invoice.period_start or not invoice.period_end:
                    continue
                actual_days = (invoice.period_end - invoice.period_start).days
                if abs(actual_days - expected_days) <= 7:
                    continue
                trace = FinancialCalculator.compute_zero_leakage(semantics="operational")
                findings.append(
                    make_result(
                        scope=scope_from_subscription(sub, invoice),
                        expected=__import__("decimal").Decimal(str(expected_days)),
                        actual=__import__("decimal").Decimal(str(actual_days)),
                        difference=__import__("decimal").Decimal(str(abs(actual_days - expected_days))),
                        calculation=trace,
                        severity="medium",
                        confidence=CONFIDENCE_MEDIUM,
                        recommendation=self.spec.recommendation_template,
                        evidence=[
                            EvidenceInput(
                                field="billing_interval",
                                expected=str(expected_days),
                                actual=str(actual_days),
                                reference_ids={"subscription_interval": sub_interval},
                            )
                        ],
                    )
                )
                break
        return findings


rule = BillingFrequencyMismatchRule()
