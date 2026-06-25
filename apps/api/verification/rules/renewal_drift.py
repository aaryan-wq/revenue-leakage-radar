from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_MEDIUM, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "renewal_price_drift"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for sub in ctx.subscriptions:
        if not sub.renewal_date or not sub.price:
            continue

        invoices = sorted(
            ctx.invoices_for_subscription(sub.id),
            key=lambda i: i.invoice_date or i.period_start or sub.renewal_date,
        )
        if len(invoices) < 2:
            continue

        prior = invoices[-2]
        renewal = invoices[-1]
        if not renewal.total or not prior.total:
            continue

        expected = prior.total
        actual = renewal.total
        if actual >= expected:
            continue

        monthly, annual = compute_leakage(expected, actual, 1, sub.billing_interval)
        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Renewal price below prior period",
                severity="medium",
                confidence=CONFIDENCE_MEDIUM,
                customer_id=str(sub.customer_id),
                subscription_id=str(sub.id),
                invoice_id=str(renewal.id),
                expected_value=expected,
                actual_value=actual,
                delta=expected - actual,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Verify renewal uplift was applied per pricing policy.",
                evidence=[
                    EvidenceRecord(
                        field="renewal_total",
                        expected=str(expected),
                        actual=str(actual),
                        reference_ids={
                            "prior_invoice": prior.invoice_number,
                            "renewal_invoice": renewal.invoice_number,
                        },
                    )
                ],
            )
        )

    return findings
