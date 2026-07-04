#!/usr/bin/env python3
"""Generate internally consistent AcmeCRM Stripe-like CSV fixtures with injected leakage."""

from __future__ import annotations

import csv
import json
import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

RNG = random.Random(42)

OUTPUT_DIR = Path(__file__).resolve().parent.parent / "testdata" / "acmecrm"

HISTORY_START = date(2023, 6, 1)
HISTORY_END = date(2025, 6, 1)
CATALOG_V1 = date(2023, 1, 1)
CATALOG_V2 = date(2024, 7, 1)

CUSTOMER_COUNT = 300
SUBSCRIPTION_COUNT = 450


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
    Plan("Ultimate", "prod_ultimate_mo", "prod_ultimate_yr", "SKU-ULT", 999, 9990),
]

V2_INCREASE = Decimal("1.15")


def money(value: Decimal | float | int) -> str:
    return str(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def add_months(d: date, months: int = 1) -> date:
    month = d.month - 1 + months
    year = d.year + month // 12
    month = month % 12 + 1
    day = min(d.day, [31, 29 if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0) else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
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
        for interval, product_id in (
            ("monthly", plan.product_monthly),
            ("annual", plan.product_annual),
        ):
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
            "expires_at": "2025-12-31",
            "active": "true",
        },
        {
            "coupon_id": "cpn_refer10",
            "code": "REFER10",
            "discount_type": "percent",
            "discount_value": "10",
            "expires_at": "2025-12-31",
            "active": "true",
        },
        {
            "coupon_id": "cpn_annual100",
            "code": "ANNUAL100",
            "discount_type": "fixed",
            "discount_value": "100.00",
            "expires_at": "2025-12-31",
            "active": "true",
        },
    ]


def build_customers() -> list[dict]:
    industries = ["SaaS", "Fintech", "Healthcare", "Retail", "Manufacturing", "Media"]
    rows: list[dict] = []
    for index in range(1, CUSTOMER_COUNT + 1):
        customer_id = f"cust_{index:04d}"
        rows.append(
            {
                "customer_id": customer_id,
                "name": f"AcmeCRM Customer {index:04d} ({RNG.choice(industries)})",
                "crm_id": f"crm_acc_{index:04d}",
            }
        )
    return rows


def assign_customers_to_subscriptions() -> list[str]:
    customer_ids = [f"cust_{index:04d}" for index in range(1, CUSTOMER_COUNT + 1)]
    assignments: list[str] = []
    double_sub_customers = set(RNG.sample(customer_ids, 150))
    for customer_id in customer_ids:
        assignments.append(customer_id)
        if customer_id in double_sub_customers:
            assignments.append(customer_id)
    while len(assignments) < SUBSCRIPTION_COUNT:
        assignments.append(RNG.choice(customer_ids))
    return assignments[:SUBSCRIPTION_COUNT]


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
        "invoice_mismatch_targets": [],
    }

    for index in range(SUBSCRIPTION_COUNT):
        sub_id = f"sub_{index + 1:04d}"
        customer_id = customer_assignments[index]
        plan = plan_for_index(index)
        interval = "monthly" if index % 5 != 0 else "annual"
        product_id = plan.product_monthly if interval == "monthly" else plan.product_annual
        start = subscription_start_date(index)
        quantity = RNG.randint(1, 25)

        if interval == "monthly":
            renewal = add_months(start, 1)
        else:
            renewal = add_years(start, 1)

        status_roll = RNG.random()
        if status_roll < 0.88:
            status = "active"
            end_date = HISTORY_END
        elif status_roll < 0.94:
            status = "canceled"
            end_date = min(HISTORY_END, start + timedelta(days=RNG.randint(90, 540)))
        else:
            status = "trialing"
            end_date = HISTORY_END

        list_v2 = catalog_price(plan, interval, "v2")
        list_v1 = catalog_price(plan, interval, "v1")
        coupon_id = ""
        price = list_v2
        scenario = "healthy"

        if index < 15:
            scenario = "expired_discount"
            coupon_id = "LAUNCH20"
            price = (list_v2 * Decimal("0.80")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            start = date(2023, 8, 1)
            renewal = add_years(start, 1) if interval == "annual" else add_months(start, 1)
            status = "active"
            end_date = HISTORY_END
            meta["expired_discount"].append(sub_id)
        elif index < 25:
            scenario = "legacy_pricing"
            start = date(2023, 9, 1) + timedelta(days=index * 3)
            price = list_v1
            renewal = add_months(CATALOG_V2, 1) if interval == "monthly" else add_years(CATALOG_V2, 1)
            status = "active"
            end_date = HISTORY_END
            meta["legacy_pricing"].append(sub_id)
        elif index < 30:
            scenario = "duplicate_discount"
            coupon_id = "PARTNER15"
            price = (list_v2 * Decimal("0.85")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            status = "active"
            end_date = HISTORY_END
            meta["duplicate_discount"].append(sub_id)
        elif index < 42:
            scenario = "undercharged"
            discount_factor = Decimal(str(RNG.uniform(0.80, 0.90))).quantize(Decimal("0.01"))
            price = (list_v2 * discount_factor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            start = date(2023, 6, 1) + timedelta(days=index * 5)
            renewal = add_years(start, 1) if interval == "annual" else add_months(start, 1)
            status = "active"
            end_date = HISTORY_END
            meta["undercharged"].append(sub_id)
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
    meta["invoice_mismatch_targets"] = [row["subscription_id"] for row in RNG.sample(healthy, 8)]

    public_rows = [{k: v for k, v in row.items() if not k.startswith("_")} for row in rows]
    return public_rows, rows, meta


def invoice_schedule(start: date, interval: str, end: date) -> list[date]:
    dates: list[date] = []
    current = start
    while current <= end:
        dates.append(current)
        current = add_months(current) if interval == "monthly" else add_years(current)
    return dates


def build_invoices_and_line_items(
    subscriptions: list[dict],
    meta: dict,
) -> tuple[list[dict], list[dict]]:
    invoices: list[dict] = []
    line_items: list[dict] = []
    invoice_counter = 1
    line_counter = 1

    last_invoice_by_sub: dict[str, str] = {}
    mismatch_targets = set(meta["invoice_mismatch_targets"])

    for sub in subscriptions:
        sub_id = sub["subscription_id"]
        interval = sub["billing_interval"]
        start = date.fromisoformat(sub["start_date"])
        end = date.fromisoformat(sub["_end_date"])
        if sub["status"] == "canceled":
            end = min(end, start + timedelta(days=RNG.randint(120, 480)))

        unit_price = Decimal(sub["price"])
        quantity = int(sub["quantity"])
        scenario = sub["_scenario"]
        coupon_id = sub.get("coupon_id") or ""
        sku = sub["_sku"]

        schedule = invoice_schedule(start, interval, end)
        for invoice_date in schedule:
            invoice_id = f"inv_{invoice_counter:06d}"
            invoice_number = f"ACME-INV-{invoice_counter:06d}"
            period_start = invoice_date
            period_end = add_months(invoice_date) if interval == "monthly" else add_years(invoice_date)

            subtotal = (unit_price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            discount = Decimal("0.00")

            if scenario == "expired_discount" and coupon_id == "LAUNCH20":
                if invoice_date > date(2024, 3, 31):
                    discount = (subtotal * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                elif invoice_date >= date(2023, 8, 1):
                    discount = (subtotal * Decimal("0.20")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            elif scenario == "duplicate_discount" and coupon_id:
                discount = (subtotal * Decimal("0.10")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            total = (subtotal - discount).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

            invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": sub["customer_id"],
                    "subscription_id": sub_id,
                    "invoice_number": invoice_number,
                    "invoice_date": invoice_date.isoformat(),
                    "period_start": period_start.isoformat(),
                    "period_end": period_end.isoformat(),
                    "subtotal": money(subtotal),
                    "discount": money(discount),
                    "total": money(total),
                    "currency": "USD",
                    "credit_amount": "0.00",
                }
            )

            line_unit_price = unit_price
            is_last = invoice_date == schedule[-1]
            if sub_id in mismatch_targets and is_last:
                line_unit_price = (unit_price * Decimal("0.88")).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )

            extended = (line_unit_price * quantity).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            line_items.append(
                {
                    "line_item_id": f"li_{line_counter:07d}",
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
                    "is_manual_override": "false",
                }
            )

            last_invoice_by_sub[sub_id] = invoice_id
            invoice_counter += 1
            line_counter += 1

    meta["invoice_mismatch_invoice_ids"] = [
        last_invoice_by_sub[sub_id] for sub_id in meta["invoice_mismatch_targets"] if sub_id in last_invoice_by_sub
    ]

    return invoices, line_items


def build_manifest(meta: dict, counts: dict) -> dict:
    return {
        "company": "AcmeCRM",
        "description": "Synthetic Stripe-like billing export with intentional revenue leakage scenarios",
        "history": {"start": HISTORY_START.isoformat(), "end": HISTORY_END.isoformat()},
        "counts": counts,
        "injected_scenarios": {
            "expired_discount_still_applied": {
                "count": len(meta["expired_discount"]),
                "subscription_ids": meta["expired_discount"],
                "rule_id": "expired_discount_still_applied",
                "notes": "LAUNCH20 coupon expired 2024-03-31; post-expiry invoices still carry discount.",
            },
            "legacy_pricing_after_renewal": {
                "count": len(meta["legacy_pricing"]),
                "subscription_ids": meta["legacy_pricing"],
                "rule_id": "legacy_sku_pricing_drift",
                "notes": "Subscriptions renewed after catalog v2 (2024-07-01) but remain on v1 list prices.",
            },
            "invoice_line_item_price_mismatch": {
                "count": len(meta["invoice_mismatch_targets"]),
                "subscription_ids": meta["invoice_mismatch_targets"],
                "rule_id": "invoice_subscription_price_mismatch",
                "notes": "Most recent invoice line item unit_price differs from subscription price.",
            },
            "duplicate_discount_stacking": {
                "count": len(meta["duplicate_discount"]),
                "subscription_ids": meta["duplicate_discount"],
                "rule_id": "duplicate_discount_stacking",
                "notes": "Active coupon on subscription plus additional invoice-level discount.",
            },
            "undercharged_subscriptions": {
                "count": len(meta["undercharged"]),
                "subscription_ids": meta["undercharged"],
                "rule_id": "grandfathered_without_contract",
                "notes": "Active subscriptions priced 10-20% below current catalog without CRM contract exception.",
            },
        },
    }


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    customers = build_customers()
    customer_assignments = assign_customers_to_subscriptions()
    subscription_rows, subscriptions_internal, meta = build_subscriptions(customer_assignments)

    invoices, line_items = build_invoices_and_line_items(subscriptions_internal, meta)
    price_catalog = build_price_catalog()
    coupons = build_coupons()

    write_csv(
        OUTPUT_DIR / "customers.csv",
        ["customer_id", "name", "crm_id"],
        customers,
    )
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
        [
            "product_id",
            "sku",
            "version",
            "effective_date",
            "list_price",
            "currency",
            "billing_interval",
        ],
        price_catalog,
    )
    write_csv(
        OUTPUT_DIR / "coupons.csv",
        ["coupon_id", "code", "discount_type", "discount_value", "expires_at", "active"],
        coupons,
    )

    counts = {
        "customers": len(customers),
        "subscriptions": len(subscription_rows),
        "invoices": len(invoices),
        "invoice_line_items": len(line_items),
        "price_catalog_entries": len(price_catalog),
        "coupons": len(coupons),
    }
    manifest = build_manifest(meta, counts)
    (OUTPUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print(f"Wrote AcmeCRM dataset to {OUTPUT_DIR}")
    for key, value in counts.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    main()
