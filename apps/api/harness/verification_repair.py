"""Repair non-injected subscriptions after verification injections."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from harness.company_state import CompanyState
from harness.money import add_months, money
from harness.types import GroundTruthFinding


def _seat_injected_customers(ground_truth: list[GroundTruthFinding]) -> set[str]:
    return {
        finding.customer_id
        for finding in ground_truth
        if finding.rule_id == "incorrect_seat_price" and finding.customer_id
    }


def repair_baseline_after_injections(
    state: CompanyState,
    injected_subscriptions: set[str],
    ground_truth: list[GroundTruthFinding] | None = None,
) -> None:
    """Keep non-injected subscriptions internally consistent so only injections leak."""
    anchor = state.anchor_date
    seat_injected = _seat_injected_customers(ground_truth or state.ground_truth)

    for sub in state.subscriptions:
        sub_id = sub["subscription_id"]
        if sub_id in injected_subscriptions:
            continue
        quantity = int(sub.get("quantity") or 1)
        unit_price = Decimal(sub["price"])
        for invoice in state.invoices_for_subscription(sub_id):
            line_items = state.line_items_for_invoice(invoice["invoice_id"])
            subtotal = Decimal("0")
            for line_item in line_items:
                if line_item.get("subscription_id") != sub_id:
                    continue
                if str(line_item.get("is_manual_override", "")).lower() == "true":
                    continue
                line_item["quantity"] = quantity
                line_item["unit_price"] = money(unit_price)
                extended = (unit_price * quantity).quantize(Decimal("0.01"))
                line_item["extended_price"] = money(extended)
                subtotal += extended
            if line_items:
                invoice["subtotal"] = money(subtotal)
                invoice["discount"] = invoice.get("discount") or "0.00"
                invoice["total"] = money(subtotal - Decimal(invoice.get("discount") or "0"))

    for account in state.crm_accounts:
        if account["customer_id"] in seat_injected:
            continue
        active_subs = [
            candidate
            for candidate in state.subscriptions
            if candidate["customer_id"] == account["customer_id"]
            and (candidate.get("status") or "").lower() == "active"
        ]
        if active_subs:
            quantities = [int(candidate.get("quantity") or 1) for candidate in active_subs]
            account["seat_count"] = quantities[0] if len(quantities) == 1 else max(quantities)

    if anchor is not None:
        _extend_invoice_history_to_anchor(state, injected_subscriptions, anchor)


def _extend_invoice_history_to_anchor(
    state: CompanyState,
    injected_subscriptions: set[str],
    anchor: date,
) -> None:
    from harness.money import invoice_schedule

    invoice_counter = max(
        (int(inv["invoice_id"].split("_")[-1]) for inv in state.invoices if inv["invoice_id"].startswith("inv_")),
        default=0,
    ) + 1
    line_counter = max(
        (int(li["line_item_id"].split("_")[-1]) for li in state.line_items if li["line_item_id"].startswith("li_")),
        default=0,
    ) + 1

    for sub in state.subscriptions:
        if (sub.get("status") or "").lower() != "active":
            continue
        sub_id = sub["subscription_id"]
        if sub_id in injected_subscriptions:
            continue
        invoices = sorted(
            state.invoices_for_subscription(sub_id),
            key=lambda row: row.get("invoice_date") or "",
        )
        if not invoices:
            continue
        last = invoices[-1]
        last_period_end = date.fromisoformat(str(last.get("period_end") or last["invoice_date"])[:10])
        if last_period_end >= anchor:
            continue
        start = add_months(date.fromisoformat(str(last["invoice_date"])[:10]))
        interval = sub.get("billing_interval") or "monthly"
        product_id = sub.get("product_id") or ""
        plan = sub.get("_plan")
        line_sku = (
            plan.sku_monthly
            if plan and interval == "monthly"
            else (plan.sku_annual if plan else sub.get("sku", ""))
        )
        unit_price = Decimal(sub["price"])
        quantity = int(sub.get("quantity") or 1)
        schedule = invoice_schedule(start, interval, anchor)
        for inv_index, invoice_date in enumerate(schedule):
            invoice_id = f"inv_{invoice_counter:07d}"
            subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
            is_last = inv_index == len(schedule) - 1
            period_end = max(add_months(invoice_date), anchor) if is_last else add_months(invoice_date)
            state.invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": sub["customer_id"],
                    "subscription_id": sub_id,
                    "invoice_number": f"INV-{invoice_counter:07d}",
                    "invoice_date": invoice_date.isoformat(),
                    "period_start": invoice_date.isoformat(),
                    "period_end": period_end.isoformat(),
                    "subtotal": money(subtotal),
                    "discount": "0.00",
                    "total": money(subtotal),
                    "currency": sub.get("currency") or state.profile.currency,
                    "credit_amount": "0.00",
                }
            )
            state.line_items.append(
                {
                    "line_item_id": f"li_{line_counter:08d}",
                    "invoice_id": invoice_id,
                    "customer_id": sub["customer_id"],
                    "subscription_id": sub_id,
                    "product_id": product_id,
                    "sku": line_sku,
                    "quantity": quantity,
                    "unit_price": money(unit_price),
                    "extended_price": money(subtotal),
                    "billing_interval": interval,
                    "line_item_date": invoice_date.isoformat(),
                    "currency": sub.get("currency") or state.profile.currency,
                    "is_manual_override": "false",
                }
            )
            invoice_counter += 1
            line_counter += 1
