from collections import defaultdict

from verification.context import AuditContext
from verification.financial import CONFIDENCE_HIGH
from verification.types import EvidenceRecord, RuleFinding

RULE_ID = "duplicate_active_subscriptions"


def evaluate(ctx: AuditContext) -> list[RuleFinding]:
    findings: list[RuleFinding] = []
    active_statuses = {"active", "trialing", "past_due"}

    groups: dict[tuple[str, str], list] = defaultdict(list)
    for sub in ctx.subscriptions:
        if not sub.product_id:
            continue
        status = (sub.status or "").lower()
        if status not in active_statuses:
            continue
        groups[(str(sub.customer_id), sub.product_id)].append(sub)

    for (customer_id, product_id), subs in groups.items():
        if len(subs) < 2:
            continue

        price = subs[0].price or 0
        monthly_loss = price
        annual_loss = monthly_loss * 12

        findings.append(
            RuleFinding(
                rule_id=RULE_ID,
                title="Duplicate active subscriptions",
                severity="high",
                confidence=CONFIDENCE_HIGH,
                customer_id=customer_id,
                subscription_id=str(subs[0].id),
                expected_value=price,
                actual_value=0,
                estimated_monthly_loss=monthly_loss,
                estimated_arr_loss=annual_loss,
                recommendation="Consolidate duplicate active subscriptions for the same product.",
                evidence=[
                    EvidenceRecord(
                        field="duplicate_subscriptions",
                        expected="1 active subscription",
                        actual=f"{len(subs)} active",
                        reference_ids={
                            "product_id": product_id,
                            "subscription_ids": ",".join(str(s.id) for s in subs),
                        },
                    )
                ],
            )
        )

    return findings
