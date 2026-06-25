from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH, compute_leakage
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "legacy_sku_pricing_drift"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []

    for sub in ctx.subscriptions:
        if not sub.product_id or not sub.price:
            continue

        latest = ctx.latest_catalog_version(sub.product_id)
        if not latest or not latest.list_price or not latest.version:
            continue

        billed_catalog = ctx.catalog_for_product(sub.product_id, as_of=sub.start_date)
        if not billed_catalog or not billed_catalog.version:
            continue
        if billed_catalog.version == latest.version:
            continue
        if sub.price >= latest.list_price:
            continue

        monthly, annual = compute_leakage(
            latest.list_price, sub.price, sub.quantity or 1, sub.billing_interval
        )
        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Legacy SKU pricing drift",
                severity="medium",
                confidence=CONFIDENCE_HIGH,
                customer_id=str(sub.customer_id),
                subscription_id=str(sub.id),
                expected_value=latest.list_price,
                actual_value=sub.price,
                delta=latest.list_price - sub.price,
                estimated_monthly_loss=monthly,
                estimated_arr_loss=annual,
                recommendation="Migrate subscription to latest SKU/catalog version pricing.",
                evidence=[
                    EvidenceRecord(
                        field="sku_version",
                        expected=latest.version,
                        actual=billed_catalog.version,
                        reference_ids={"product_id": sub.product_id},
                    )
                ],
            )
        )

    return findings
