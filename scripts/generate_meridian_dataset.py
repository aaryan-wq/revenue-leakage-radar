#!/usr/bin/env python3
"""Generate Meridian Platform CSV fixtures — realistic $25M ARR mid-market SaaS."""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RNG = random.Random(20250831)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "testdata" / "meridian_platform"

HISTORY_START = date(2023, 6, 1)
HISTORY_END = date(2025, 8, 1)
CATALOG_V1 = date(2023, 1, 1)
CATALOG_V2 = date(2024, 7, 1)

CUSTOMER_COUNT = 450
SUBSCRIPTION_COUNT = 470

# Small, targeted leakage injections (~3% of ARR when audited).
INJECT_EXPIRED_DISCOUNT = 6
INJECT_LEGACY_PRICING = 3
INJECT_DUPLICATE_DISCOUNT = 3
INJECT_UNDERCHARGED = 6
INJECT_CANCELLED_STILL_BILLING = 2
INJECT_MIGRATION_DUPES = 20
INJECT_INVOICE_MISMATCH = 5
INJECT_MANUAL_OVERRIDE = 4

INJECT_END = (
    INJECT_EXPIRED_DISCOUNT
    + INJECT_LEGACY_PRICING
    + INJECT_DUPLICATE_DISCOUNT
    + INJECT_UNDERCHARGED
    + INJECT_CANCELLED_STILL_BILLING
)


@dataclass(frozen=True)
class Plan:
    tier: str
    product_monthly: str
    product_annual: str
    sku: str
    monthly_price: int
    annual_price: int


PLANS: list[Plan] = [
    Plan("Starter", "prod_starter_mo", "prod_starter_yr", "SKU-STARTER", 49, 490),
    Plan("Growth", "prod_growth_mo", "prod_growth_yr", "SKU-GROWTH", 99, 990),
    Plan("Professional", "prod_professional_mo", "prod_professional_yr", "SKU-PRO", 199, 1990),
    Plan("Business", "prod_business_mo", "prod_business_yr", "SKU-BIZ", 399, 3990),
    Plan("Enterprise", "prod_enterprise_mo", "prod_enterprise_yr", "SKU-ENT", 699, 6990),
]

V2_INCREASE = Decimal("1.12")


def money(value: Decimal | float | int) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def add_months(d: date, months: int = 1) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(
        d.day,
        [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][
            month - 1
        ],
    )
    return date(year, month, day)


def add_years(d: date, years: int = 1) -> date:
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d.replace(year=d.year + years, day=28)


def catalog_price(plan: Plan, interval: str, version: str) -> Decimal:
    base = Decimal(plan.monthly_price if interval == "monthly" else plan.annual_price)
    if version == "v2":
        return (base * V2_INCREASE).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return base


def plan_for_index(index: int) -> Plan:
    return PLANS[index % len(PLANS)]


def write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def build_price_catalog() -> list[dict]:
    rows: list[dict] = []
    for plan in PLANS:
        for interval, product_id in (("monthly", plan.product_monthly), ("annual", plan.product_annual)):
            for version, effective in (("v1", CATALOG_V1), ("v2", CATALOG_V2)):
                rows.append(
                    {
                        "product_id": product_id,
                        "sku": plan.sku,
                        "version": version,
                        "effective_date": effective.isoformat(),
                        "list_price": money(catalog_price(plan, interval, version)),
                        "currency": "USD",
                        "billing_interval": interval,
                    }
                )
    return rows


def build_coupons() -> list[dict]:
    return [
        {
            "coupon_id": "cpn_eoy25",
            "code": "EOY25",
            "discount_type": "percent",
            "discount_value": "20",
            "expires_at": "2025-03-31",
            "active": "true",
        },
        {
            "coupon_id": "cpn_partner15",
            "code": "PARTNER15",
            "discount_type": "percent",
            "discount_value": "15",
            "expires_at": "2025-12-31",
            "active": "true",
        },
    ]


def build_customers() -> list[dict]:
    industries = ["SaaS", "Fintech", "Healthcare", "Manufacturing", "Logistics"]
    return [
        {
            "customer_id": f"mer_cust_{index:04d}",
            "name": f"Meridian Customer {index:04d} ({RNG.choice(industries)})",
            "crm_id": f"sf_acc_{index:04d}",
        }
        for index in range(1, CUSTOMER_COUNT + 1)
    ]


def assign_customers_to_subscriptions() -> list[str]:
    customer_ids = [f"mer_cust_{index:04d}" for index in range(1, CUSTOMER_COUNT + 1)]
    migration_dupes = set(RNG.sample(customer_ids, INJECT_MIGRATION_DUPES))
    assignments: list[str] = []
    for customer_id in customer_ids:
        assignments.append(customer_id)
        if customer_id in migration_dupes:
            assignments.append(customer_id)
    return assignments


def subscription_start_date(index: int) -> date:
    offset_days = int((index / SUBSCRIPTION_COUNT) * (HISTORY_END - HISTORY_START).days)
    return HISTORY_START + timedelta(days=offset_days)


def build_subscriptions(customer_assignments: list[str]) -> tuple[list[dict], list[dict], dict]:
    rows: list[dict] = []
    meta: dict = {
        "expired_discount": [],
        "legacy_pricing": [],
        "duplicate_discount": [],
        "undercharged": [],
        "cancelled_still_billing": [],
        "invoice_mismatch_targets": [],
        "manual_override_targets": [],
        "migration_duplicates": [],
    }

    idx = 0
    expired_end = idx + INJECT_EXPIRED_DISCOUNT
    legacy_end = expired_end + INJECT_LEGACY_PRICING
    dup_disc_end = legacy_end + INJECT_DUPLICATE_DISCOUNT
    under_end = dup_disc_end + INJECT_UNDERCHARGED
    cancel_end = under_end + INJECT_CANCELLED_STILL_BILLING

    customer_quantity: dict[str, int] = {}

    for index in range(SUBSCRIPTION_COUNT):
        sub_id = f"mer_sub_{index + 1:04d}"
        customer_id = customer_assignments[index]
        plan = plan_for_index(index)
        interval = "monthly" if index % 5 != 0 else "annual"
        product_id = plan.product_monthly if interval == "monthly" else plan.product_annual
        start = subscription_start_date(index)
        if customer_id in customer_quantity:
            quantity = customer_quantity[customer_id]
        else:
            quantity = RNG.randint(1, 25)
            customer_quantity[customer_id] = quantity
        renewal = add_months(start, 1) if interval == "monthly" else add_years(start, 1)

        status_roll = RNG.random()
        if status_roll < 0.92:
            status = "active"
            end_date = HISTORY_END
        elif status_roll < 0.97:
            status = "canceled"
            end_date = min(HISTORY_END, start + timedelta(days=RNG.randint(90, 540)))
            renewal = end_date
        else:
            status = "trialing"
            end_date = HISTORY_END

        list_v2 = catalog_price(plan, interval, "v2")
        list_v1 = catalog_price(plan, interval, "v1")
        coupon_id = ""
        price = list_v2
        scenario = "healthy"

        if index < expired_end:
            scenario = "expired_discount"
            coupon_id = "EOY25"
            price = (list_v2 * Decimal("0.80")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            start = date(2025, 4, 1)
            renewal = add_months(start, 1) if interval == "monthly" else add_years(start, 1)
            status = "active"
            end_date = HISTORY_END
            meta["expired_discount"].append(sub_id)
        elif index < legacy_end:
            scenario = "legacy_pricing"
            start = date(2023, 9, 1) + timedelta(days=(index - expired_end) * 3)
            price = list_v1
            renewal = add_months(CATALOG_V2, 1) if interval == "monthly" else add_years(CATALOG_V2, 1)
            status = "active"
            end_date = HISTORY_END
            meta["legacy_pricing"].append(sub_id)
        elif index < dup_disc_end:
            scenario = "duplicate_discount"
            coupon_id = "PARTNER15"
            price = (list_v2 * Decimal("0.85")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            start = date(2025, 5, 1)
            renewal = add_months(start, 1) if interval == "monthly" else add_years(start, 1)
            status = "active"
            end_date = HISTORY_END
            meta["duplicate_discount"].append(sub_id)
        elif index < under_end:
            scenario = "undercharged"
            discount_factor = Decimal(str(RNG.uniform(0.85, 0.92))).quantize(Decimal("0.01"))
            price = (list_v2 * discount_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            start = date(2023, 6, 1) + timedelta(days=(index - dup_disc_end) * 5)
            renewal = add_months(start, 1) if interval == "monthly" else add_years(start, 1)
            status = "active"
            end_date = HISTORY_END
            meta["undercharged"].append(sub_id)
        elif index < cancel_end:
            scenario = "cancelled_still_billing"
            status = "canceled"
            end_date = date(2025, 6, 1) + timedelta(days=index)
            renewal = end_date
            meta["cancelled_still_billing"].append(sub_id)
        else:
            price = list_v2
            if start < CATALOG_V2 and status == "canceled":
                price = list_v1

        rows.append(
            {
                "subscription_id": sub_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "plan": plan.tier,
                "quantity": quantity,
                "billing_interval": interval,
                "price": money(price),
                "currency": "USD",
                "start_date": start.isoformat(),
                "renewal_date": renewal.isoformat(),
                "status": status,
                "coupon_id": coupon_id,
                "_scenario": scenario,
                "_end_date": end_date.isoformat(),
                "_sku": plan.sku,
            }
        )

    healthy = [row for row in rows if row["_scenario"] == "healthy" and row["status"] == "active"]
    meta["invoice_mismatch_targets"] = [row["subscription_id"] for row in RNG.sample(healthy, INJECT_INVOICE_MISMATCH)]
    meta["manual_override_targets"] = [row["subscription_id"] for row in RNG.sample(healthy, INJECT_MANUAL_OVERRIDE)]

    customer_sub_counts: dict[str, int] = {}
    for row in rows:
        if row["status"] == "active":
            customer_sub_counts[row["customer_id"]] = customer_sub_counts.get(row["customer_id"], 0) + 1
    meta["migration_duplicates"] = [cid for cid, count in customer_sub_counts.items() if count > 1]

    public_rows = [{key: value for key, value in row.items() if not key.startswith("_")} for row in rows]
    return public_rows, rows, meta


def invoice_schedule(start: date, interval: str, end: date) -> list[date]:
    dates: list[date] = []
    current = start
    while current <= end:
        dates.append(current)
        current = add_months(current) if interval == "monthly" else add_years(current)
    return dates


def build_invoices_and_line_items(subscriptions: list[dict], meta: dict) -> tuple[list[dict], list[dict]]:
    invoices: list[dict] = []
    line_items: list[dict] = []
    invoice_counter = 1
    line_counter = 1
    mismatch_targets = set(meta["invoice_mismatch_targets"])
    manual_targets = set(meta["manual_override_targets"])

    for sub in subscriptions:
        sub_id = sub["subscription_id"]
        interval = sub["billing_interval"]
        start = date.fromisoformat(sub["start_date"])
        end = date.fromisoformat(sub["_end_date"])
        renewal = date.fromisoformat(sub["renewal_date"])
        if sub["status"] == "canceled" and sub["_scenario"] != "cancelled_still_billing":
            end = min(end, renewal)

        unit_price = Decimal(sub["price"])
        quantity = int(sub["quantity"])
        scenario = sub["_scenario"]
        coupon_id = sub.get("coupon_id") or ""
        sku = sub["_sku"]

        schedule = invoice_schedule(start, interval, end)
        if scenario == "cancelled_still_billing":
            extra = add_months(renewal, 1) if interval == "monthly" else add_years(renewal, 1)
            if extra <= HISTORY_END:
                schedule.append(extra)

        for invoice_date in schedule:
            invoice_id = f"mer_inv_{invoice_counter:06d}"
            subtotal = (unit_price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            discount = Decimal("0.00")

            if scenario == "expired_discount" and coupon_id == "EOY25" and invoice_date >= date(2025, 4, 1):
                discount = (subtotal * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            elif scenario == "duplicate_discount" and coupon_id and invoice_date >= date(2025, 6, 1):
                discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            total = (subtotal - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": sub["customer_id"],
                    "subscription_id": sub_id,
                    "invoice_number": f"MER-INV-{invoice_counter:06d}",
                    "invoice_date": invoice_date.isoformat(),
                    "period_start": invoice_date.isoformat(),
                    "period_end": (add_months(invoice_date) if interval == "monthly" else add_years(invoice_date)).isoformat(),
                    "subtotal": money(subtotal),
                    "discount": money(discount),
                    "total": money(total),
                    "currency": "USD",
                    "credit_amount": "0.00",
                }
            )

            line_unit_price = unit_price
            is_last = invoice_date == schedule[-1]
            is_manual = "false"
            if sub_id in mismatch_targets and is_last:
                line_unit_price = (unit_price * Decimal("0.92")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            if sub_id in manual_targets and is_last:
                is_manual = "true"

            extended = (line_unit_price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            line_items.append(
                {
                    "line_item_id": f"mer_li_{line_counter:07d}",
                    "invoice_id": invoice_id,
                    "customer_id": sub["customer_id"],
                    "subscription_id": sub_id,
                    "product_id": sub["product_id"],
                    "sku": sku,
                    "quantity": quantity,
                    "unit_price": money(line_unit_price),
                    "extended_price": money(extended),
                    "billing_interval": interval,
                    "line_item_date": invoice_date.isoformat(),
                    "currency": "USD",
                    "is_manual_override": is_manual,
                }
            )
            invoice_counter += 1
            line_counter += 1

    return invoices, line_items


def build_crm_accounts(customers: list[dict], subscriptions: list[dict]) -> list[dict]:
    sub_by_customer: dict[str, list[dict]] = {}
    for sub in subscriptions:
        sub_by_customer.setdefault(sub["customer_id"], []).append(sub)
    return [
        {
            "account_id": customer["crm_id"],
            "customer_id": customer["customer_id"],
            "name": customer["name"],
            "seat_count": max(
                (int(s["quantity"]) for s in sub_by_customer.get(customer["customer_id"], []) if s["status"] == "active"),
                default=1,
            ),
        }
        for customer in customers
    ]


def build_crm_contracts(subscriptions: list[dict], meta: dict) -> list[dict]:
    rows: list[dict] = []
    undercharged_ids = set(meta["undercharged"])
    contract_counter = 1
    for sub in subscriptions:
        if sub["status"] != "active" or sub["subscription_id"] not in undercharged_ids:
            continue
        quantity = int(sub["quantity"])
        billing_price = Decimal(sub["price"])
        interval = sub["billing_interval"]
        factor = Decimal("12") if interval == "monthly" else Decimal("1")
        contract_annual = (billing_price * quantity * factor * Decimal("1.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        start = date.fromisoformat(sub["start_date"])
        rows.append(
            {
                "contract_id": f"mer_ctr_{contract_counter:04d}",
                "account_id": f"sf_acc_{sub['customer_id'].split('_')[-1]}",
                "contract_price": money(contract_annual),
                "price_increase_date": add_years(start, 1).isoformat(),
                "expected_renewal_price": money(contract_annual * Decimal("1.05")),
                "start_date": start.isoformat(),
                "end_date": add_years(start, 1).isoformat(),
                "seat_count": quantity,
            }
        )
        contract_counter += 1
    return rows


def estimate_arr(invoices: list[dict], subscriptions: list[dict]) -> float:
    interval_by_sub = {row["subscription_id"]: row["billing_interval"] for row in subscriptions}
    latest_by_sub: dict[str, tuple[date, Decimal]] = {}
    for inv in invoices:
        inv_date = date.fromisoformat(inv["invoice_date"])
        total = Decimal(inv["total"])
        sub_id = inv["subscription_id"]
        if sub_id not in latest_by_sub or inv_date > latest_by_sub[sub_id][0]:
            latest_by_sub[sub_id] = (inv_date, total)
    annualized = Decimal("0")
    for sub_id, (_inv_date, total) in latest_by_sub.items():
        if interval_by_sub.get(sub_id) == "monthly":
            annualized += total * Decimal("12")
        else:
            annualized += total
    return float(annualized)


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = build_customers()
    customer_assignments = assign_customers_to_subscriptions()
    subscription_rows, subscriptions_internal, meta = build_subscriptions(customer_assignments)
    invoices, line_items = build_invoices_and_line_items(subscriptions_internal, meta)
    price_catalog = build_price_catalog()
    coupons = build_coupons()
    crm_accounts = build_crm_accounts(customers, subscription_rows)
    crm_contracts = build_crm_contracts(subscription_rows, meta)

    write_csv(OUTPUT_DIR / "customers.csv", ["customer_id", "name", "crm_id"], customers)
    write_csv(
        OUTPUT_DIR / "subscriptions.csv",
        [
            "subscription_id",
            "customer_id",
            "product_id",
            "plan",
            "quantity",
            "billing_interval",
            "price",
            "currency",
            "start_date",
            "renewal_date",
            "status",
            "coupon_id",
        ],
        subscription_rows,
    )
    write_csv(
        OUTPUT_DIR / "invoices.csv",
        [
            "invoice_id",
            "customer_id",
            "subscription_id",
            "invoice_number",
            "invoice_date",
            "period_start",
            "period_end",
            "subtotal",
            "discount",
            "total",
            "currency",
            "credit_amount",
        ],
        invoices,
    )
    write_csv(
        OUTPUT_DIR / "invoice_line_items.csv",
        [
            "line_item_id",
            "invoice_id",
            "customer_id",
            "subscription_id",
            "product_id",
            "sku",
            "quantity",
            "unit_price",
            "extended_price",
            "billing_interval",
            "line_item_date",
            "currency",
            "is_manual_override",
        ],
        line_items,
    )
    write_csv(
        OUTPUT_DIR / "price_catalog.csv",
        ["product_id", "sku", "version", "effective_date", "list_price", "currency", "billing_interval"],
        price_catalog,
    )
    write_csv(OUTPUT_DIR / "coupons.csv", ["coupon_id", "code", "discount_type", "discount_value", "expires_at", "active"], coupons)
    write_csv(OUTPUT_DIR / "crm_accounts.csv", ["account_id", "customer_id", "name", "seat_count"], crm_accounts)
    write_csv(
        OUTPUT_DIR / "crm_contracts.csv",
        [
            "contract_id",
            "account_id",
            "contract_price",
            "price_increase_date",
            "expected_renewal_price",
            "start_date",
            "end_date",
            "seat_count",
        ],
        crm_contracts,
    )

    counts = {
        "customers": len(customers),
        "subscriptions": len(subscription_rows),
        "invoices": len(invoices),
        "invoice_line_items": len(line_items),
        "price_catalog_entries": len(price_catalog),
        "coupons": len(coupons),
        "crm_accounts": len(crm_accounts),
        "crm_contracts": len(crm_contracts),
    }
    arr_estimate = estimate_arr(invoices, subscription_rows)
    manifest = {
        "company": "Meridian Platform",
        "profile": {"arr_target_usd": 25_000_000, "customer_count": CUSTOMER_COUNT},
        "estimated_billed_arr_usd": arr_estimate,
        "counts": counts,
        "injected_scenarios": {
            "expired_discount": len(meta["expired_discount"]),
            "legacy_pricing": len(meta["legacy_pricing"]),
            "duplicate_discount": len(meta["duplicate_discount"]),
            "undercharged": len(meta["undercharged"]),
            "cancelled_still_billing": len(meta["cancelled_still_billing"]),
            "invoice_mismatch": len(meta["invoice_mismatch_targets"]),
            "manual_override": len(meta["manual_override_targets"]),
            "migration_duplicate_customers": len(meta["migration_duplicates"]),
        },
    }
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote Meridian Platform dataset to {OUTPUT_DIR}")
    for key, value in counts.items():
        print(f"  {key}: {value}")
    print(f"  estimated_trailing_arr_usd: ${arr_estimate:,.0f}")
    print(f"  injected_leaky_subscriptions: {INJECT_END} of {SUBSCRIPTION_COUNT}")


if __name__ == "__main__":
    main()
