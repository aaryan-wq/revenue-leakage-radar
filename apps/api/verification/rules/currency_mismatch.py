from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "currency_inconsistency"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for sub in ctx.subscriptions:
        if not sub.currency:
            continue
        for invoice in ctx.invoices_for_subscription(sub.id):
            if not invoice.currency or invoice.currency.upper() == sub.currency.upper():
                continue

            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Currency inconsistency",
                    severity="high",
                    confidence=CONFIDENCE_HIGH,
                    customer_id=str(sub.customer_id),
                    subscription_id=str(sub.id),
                    invoice_id=str(invoice.id),
                    recommendation="Reconcile currency across subscription and invoice records.",
                    evidence=[
                        EvidenceRecord(
                            field="currency",
                            expected=sub.currency,
                            actual=invoice.currency,
                            reference_ids={"invoice": invoice.invoice_number},
                        )
                    ],
                )
            )

        catalog = ctx.catalog_for_product(sub.product_id)
        if catalog and catalog.currency and sub.currency:
            if catalog.currency.upper() != sub.currency.upper():
                findings.append(
                    RuleFinding(
                        rule_id=RULE_ID,
                        title="Subscription vs catalog currency mismatch",
                        severity="medium",
                        confidence=CONFIDENCE_HIGH,
                        customer_id=str(sub.customer_id),
                        subscription_id=str(sub.id),
                        recommendation="Align subscription currency with price catalog.",
                        evidence=[
                            EvidenceRecord(
                                field="currency",
                                expected=catalog.currency,
                                actual=sub.currency,
                                reference_ids={"product_id": sub.product_id or ""},
                            )
                        ],
                    )
                )

    return findings
