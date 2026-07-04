"""Leak-free baseline for verification upload datasets, injections are the only leakage."""

from __future__ import annotations

import random
from datetime import date, timedelta
from decimal import Decimal

from harness.baseline import (
    CATALOG_V2,
    VERIFICATION_ANCHOR_DATE,
    build_product_catalog,
    build_profile,
    catalog_price,
)
from harness.company_state import CompanyState
from harness.money import add_months, add_years, invoice_schedule, money


def build_clean_baseline_state(
    rng: random.Random,
    customer_count: int,
    product_count: int = 4,
    include_crm: bool = True,
) -> CompanyState:
    """Baseline company that should produce zero verification findings before injections."""
    profile = build_profile(rng, customer_count, product_count)
    plans = build_product_catalog(rng, product_count)
    history_end = VERIFICATION_ANCHOR_DATE
    state = CompanyState(profile=profile, anchor_date=history_end)

    for index in range(1, customer_count + 1):
        customer_id = f"cust_{index:05d}"
        state.customers.append(
            {
                "customer_id": customer_id,
                "name": f"{profile.name} Customer {index:05d}",
                "crm_id": f"crm_{index:05d}",
            }
        )

    state.coupons.extend(
        [
            {
                "coupon_id": "cpn_launch20",
                "code": "LAUNCH20",
                "discount_type": "percent",
                "discount_value": "20",
                "expires_at": "2024-03-31",
                "active": "true",
            },
            {
                "coupon_id": "cpn_partner15",
                "code": "PARTNER15",
                "discount_type": "percent",
                "discount_value": "15",
                "expires_at": "2026-12-31",
                "active": "true",
            },
            {
                "coupon_id": "cpn_refer10",
                "code": "REFER10",
                "discount_type": "percent",
                "discount_value": "10",
                "expires_at": "2026-12-31",
                "active": "true",
            },
        ]
    )

    # Single stable catalog version, subscriptions start after effective date at list price.
    for plan in plans:
        for interval, product_id, sku in (
            ("monthly", plan.product_monthly, plan.sku_monthly),
            ("annual", plan.product_annual, plan.sku_annual),
        ):
            state.price_catalog.append(
                {
                    "product_id": product_id,
                    "sku": sku,
                    "version": "v2",
                    "effective_date": CATALOG_V2.isoformat(),
                    "list_price": money(catalog_price(plan, interval, "v2")),
                    "currency": profile.currency,
                    "billing_interval": interval,
                }
            )

    invoice_counter = 1
    line_counter = 1
    sub_start = CATALOG_V2 + timedelta(days=30)

    for index in range(1, customer_count + 1):
        customer_id = f"cust_{index:05d}"
        plan = plans[(index - 1) % len(plans)]
        interval = "monthly"
        product_id = plan.product_monthly
        line_sku = plan.sku_monthly
        list_price = catalog_price(plan, interval, "v2")
        quantity = rng.randint(3, 12)
        start = sub_start + timedelta(days=(index % 20))
        renewal = add_months(start) if interval == "monthly" else add_years(start)
        sub_id = f"sub_{index:05d}"

        state.subscriptions.append(
            {
                "subscription_id": sub_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "plan": plan.tier,
                "quantity": quantity,
                "billing_interval": interval,
                "price": money(list_price),
                "currency": profile.currency,
                "start_date": start.isoformat(),
                "renewal_date": renewal.isoformat(),
                "status": "active",
                "coupon_id": "",
                "_plan": plan,
                "_end_date": history_end.isoformat(),
            }
        )

        if include_crm and profile.crm_platform != "none":
            state.crm_accounts.append(
                {
                    "account_id": f"acct_{index:05d}",
                    "customer_id": customer_id,
                    "name": f"Account {index:05d}",
                    "seat_count": quantity,
                }
            )

        schedule = invoice_schedule(start, interval, history_end)
        for inv_index, invoice_date in enumerate(schedule):
            invoice_id = f"inv_{invoice_counter:07d}"
            subtotal = (list_price * quantity).quantize(Decimal("0.01"))
            period_end = (
                add_months(invoice_date)
                if inv_index < len(schedule) - 1
                else max(add_months(invoice_date), history_end)
            )
            state.invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "subscription_id": sub_id,
                    "invoice_number": f"INV-{invoice_counter:07d}",
                    "invoice_date": invoice_date.isoformat(),
                    "period_start": invoice_date.isoformat(),
                    "period_end": period_end.isoformat(),
                    "subtotal": money(subtotal),
                    "discount": "0.00",
                    "total": money(subtotal),
                    "currency": profile.currency,
                    "credit_amount": "0.00",
                }
            )
            state.line_items.append(
                {
                    "line_item_id": f"li_{line_counter:08d}",
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "subscription_id": sub_id,
                    "product_id": product_id,
                    "sku": line_sku,
                    "quantity": quantity,
                    "unit_price": money(list_price),
                    "extended_price": money(subtotal),
                    "billing_interval": interval,
                    "line_item_date": invoice_date.isoformat(),
                    "currency": profile.currency,
                    "is_manual_override": "false",
                }
            )
            invoice_counter += 1
            line_counter += 1

    return state
