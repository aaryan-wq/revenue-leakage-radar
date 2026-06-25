from decimal import Decimal

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "seat_quantity_underbilling"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    if not ctx.has_crm:
        return []

    findings: list[RuleFinding] = []
    for account in ctx.crm_accounts:
        if not account.seat_count or not account.customer_id:
            continue

        subs = ctx.subscriptions_for_customer(account.customer_id)
        for sub in subs:
            if not sub.quantity or not sub.price:
                continue
            if account.seat_count <= sub.quantity:
                continue

            extra_seats = account.seat_count - sub.quantity
            monthly, annual = compute_leakage(sub.price, Decimal("0"), extra_seats, sub.billing_interval)
            monthly = (sub.price * Decimal(str(extra_seats))).quantize(Decimal("0.0001"))
            annual = (monthly * Decimal("12")).quantize(Decimal("0.0001"))

            findings.append(
                RuleFinding(
                    rule_id=RULE_ID,
                    title="Seat count underbilling",
                    severity="high",
                    confidence=CONFIDENCE_HIGH,
                    customer_id=str(sub.customer_id),
                    subscription_id=str(sub.id),
                    expected_value=Decimal(str(account.seat_count)),
                    actual_value=Decimal(str(sub.quantity)),
                    delta=Decimal(str(extra_seats)),
                    estimated_monthly_loss=monthly,
                    estimated_arr_loss=annual,
                    recommendation="Bill for full seat count per CRM account record.",
                    evidence=[
                        EvidenceRecord(
                            field="seat_count",
                            expected=str(account.seat_count),
                            actual=str(sub.quantity),
                            reference_ids={"account": account.external_account_id},
                        )
                    ],
                )
            )

    return findings
