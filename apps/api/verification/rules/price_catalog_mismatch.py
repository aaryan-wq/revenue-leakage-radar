from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "price_catalog_mismatch"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for li in ctx.line_items:
        if li.unit_price is None:
            continue
        invoice = next((i for i in ctx.invoices if i.id == li.invoice_id), None)
        if not invoice:
            continue

        catalog = ctx.catalog_for_product(li.product_id, li.sku, invoice.invoice_date)
        if not catalog or catalog.list_price is None:
            continue
        if li.unit_price == catalog.list_price:
            continue

        monthly, annual = compute_leakage(
            catalog.list_price, li.unit_price, li.quantity or 1, "monthly"
        )
        if monthly <= 0:
            continue

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Invoice line price differs from catalog",
                severity="high",
                confidence=CONFIDENCE_HIGH,
                customer_id=str(invoice.customer_id),
                invoice_id=str(invoice.id),
                expected_value=catalog.list_price,
                actual_value=li.unit_price,
                delta=catalog.list_price - li.unit_price,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Reconcile line item unit price with active price catalog entry.",
                evidence=[
                    EvidenceRecord(
                        field="unit_price",
                        expected=str(catalog.list_price),
                        actual=str(li.unit_price),
                        reference_ids={
                            "sku": li.sku or "",
                            "product_id": li.product_id or "",
                            "invoice": invoice.invoice_number,
                        },
                    )
                ],
            )
        )

    return findings
