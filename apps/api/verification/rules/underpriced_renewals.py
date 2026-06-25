from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "underpriced_renewal_vs_contract"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    if not ctx.has_crm:
        return []

    findings: list[RuleFinding] = []
    for contract in ctx.crm_contracts:
        if not contract.expected_renewal_price or not contract.customer_id:
            continue

        subs = ctx.subscriptions_for_customer(contract.customer_id)
        for sub in subs:
            invoices = sorted(
                ctx.invoices_for_subscription(sub.id),
                key=lambda i: i.invoice_date or i.period_start or sub.renewal_date,
            )
            if not invoices:
                continue
            renewal = invoices[-1]
            if not renewal.total:
                continue
            if renewal.total >= contract.expected_renewal_price:
                continue

            monthly, annual = compute_leakage(
                contract.expected_renewal_price, renewal.total, 1, sub.billing_interval
            )
            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Underpriced renewal vs contract",
                    severity="high",
                    confidence=CONFIDENCE_HIGH,
                    customer_id=str(sub.customer_id),
                    subscription_id=str(sub.id),
                    invoice_id=str(renewal.id),
                    expected_value=contract.expected_renewal_price,
                    actual_value=renewal.total,
                    delta=contract.expected_renewal_price - renewal.total,
                    estimated_monthly_loss=monthly,
                    estimated_arr_loss=annual,
                    recommendation="Apply contracted renewal price on next billing cycle.",
                    evidence=[
                        EvidenceRecord(
                            field="renewal_total",
                            expected=str(contract.expected_renewal_price),
                            actual=str(renewal.total),
                            reference_ids={
                                "contract": contract.external_contract_id,
                                "invoice": renewal.invoice_number,
                            },
                        )
                    ],
                )
            )

    return findings
