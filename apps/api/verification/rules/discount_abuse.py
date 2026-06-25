from collections import defaultdict
from datetime import datetime, timedelta, timezone
from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_MEDIUM
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "discount_abuse_frequency"
DISCOUNT_THRESHOLD = 3
ROLLING_MONTHS = 12


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=ROLLING_MONTHS * 30)

    customer_discounts: dict[str, list] = defaultdict(list)
    for invoice in ctx.invoices:
        if not invoice.discount or invoice.discount <= 0:
            continue
        if invoice.invoice_date and invoice.invoice_date.replace(tzinfo=timezone.utc) < cutoff:
            continue
        customer_discounts[str(invoice.customer_id)].append(invoice)

    for customer_id, invoices in customer_discounts.items():
        if len(invoices) < DISCOUNT_THRESHOLD:
            continue

        total_discount = sum((i.discount or Decimal("0") for i in invoices), Decimal("0"))
        monthly = (total_discount / Decimal(str(ROLLING_MONTHS))).quantize(Decimal("0.0001"))
        annual = (monthly * Decimal("12")).quantize(Decimal("0.0001"))

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Frequent discount abuse pattern",
                severity="medium",
                confidence=CONFIDENCE_MEDIUM,
                customer_id=customer_id,
                expected_value=Decimal(str(DISCOUNT_THRESHOLD)),
                actual_value=Decimal(str(len(invoices))),
                delta=Decimal(str(len(invoices) - DISCOUNT_THRESHOLD)),
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Review discount policy — customer exceeds normal discount frequency.",
                evidence=[
                    EvidenceRecord(
                        field="discount_frequency",
                        expected=f"<={DISCOUNT_THRESHOLD} in {ROLLING_MONTHS}mo",
                        actual=str(len(invoices)),
                        reference_ids={"invoice_count": str(len(invoices))},
                    )
                ],
            )
        )

    return findings
