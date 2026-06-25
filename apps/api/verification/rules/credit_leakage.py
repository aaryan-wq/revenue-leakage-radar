from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_MEDIUM
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "credit_adjustment_leakage"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    if not ctx.has_credit_data:
        return []

    findings: list[RuleFinding] = []
    for invoice in ctx.invoices:
        if not invoice.credit_amount or invoice.credit_amount <= 0:
            continue
        if invoice.total and invoice.subtotal and invoice.credit_amount > invoice.subtotal:
            monthly = invoice.credit_amount.quantize(Decimal("0.0001"))
            annual = (monthly * Decimal("12")).quantize(Decimal("0.0001"))
            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Credit adjustment leakage",
                    severity="medium",
                    confidence=CONFIDENCE_MEDIUM,
                    customer_id=str(invoice.customer_id),
                    invoice_id=str(invoice.id),
                    expected_value=invoice.subtotal,
                    actual_value=invoice.total,
                    delta=invoice.credit_amount,
                    estimated_monthly_loss=monthly,
                    estimated_arr_loss=annual,
                    recommendation="Review credit application — credits exceed invoice subtotal.",
                    evidence=[
                        EvidenceRecord(
                            field="credit_amount",
                            expected=str(invoice.subtotal),
                            actual=str(invoice.credit_amount),
                            reference_ids={"invoice": invoice.invoice_number},
                        )
                    ],
                )
            )

    return findings
