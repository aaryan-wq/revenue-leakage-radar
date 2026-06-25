from datetime import datetime, timezone
from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_MEDIUM
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "free_plan_never_converted"
FREE_STATUSES = {"free", "trial", "trialing"}
TENURE_THRESHOLD_DAYS = 90


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    now = datetime.now(timezone.utc)

    for sub in ctx.subscriptions:
        status = (sub.status or "").lower()
        plan = (sub.plan or "").lower()
        is_free = status in FREE_STATUSES or "free" in plan
        if not is_free:
            continue

        invoices = ctx.invoices_for_subscription(sub.id)
        has_paid_invoice = any(i.total and i.total > 0 for i in invoices)

        tenure_exceeded = False
        if sub.start_date:
            start = sub.start_date
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            tenure_exceeded = (now - start).days > TENURE_THRESHOLD_DAYS

        if not has_paid_invoice and not tenure_exceeded:
            continue

        catalog = ctx.catalog_for_product(sub.product_id)
        expected = catalog.list_price if catalog and catalog.list_price else Decimal("99")

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Free plan never converted",
                severity="medium",
                confidence=CONFIDENCE_MEDIUM,
                customer_id=str(sub.customer_id),
                subscription_id=str(sub.id),
                expected_value=expected,
                actual_value=Decimal("0"),
                delta=expected,
                estimated_monthly_loss=expected,
                estimated_arr_loss=expected * Decimal("12"),
                recommendation="Review free/trial subscription for monetization opportunity.",
                evidence=[
                    EvidenceRecord(
                        field="subscription_status",
                        expected="paid",
                        actual=status or plan,
                        reference_ids={"invoice_count": str(len(invoices))},
                    )
                ],
            )
        )

    return findings
