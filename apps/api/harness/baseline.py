"""Generate internally consistent baseline billing companies."""

from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal

from harness.company_state import CompanyState
from harness.money import add_months, add_years, invoice_schedule, money
from harness.types import CompanyProfile

INDUSTRIES = ["SaaS", "Fintech", "Healthcare", "Retail", "Manufacturing", "Media", "EdTech"]
BILLING_PLATFORMS = ["stripe", "chargebee", "maxio", "zuora", "paddle", "recurly"]
CRM_PLATFORMS = ["hubspot", "salesforce", "pipedrive", "attio", "none"]
CURRENCIES = ["USD", "EUR", "GBP"]
LOCALES = ["en-US", "en-GB", "de-DE", "fr-FR"]
PRICING_STRATEGIES = ["flat", "seat_based", "tiered", "usage_hybrid"]

HISTORY_START = date(2023, 1, 1)
HISTORY_END = date(2025, 6, 1)
# Fixed audit anchor for verification upload datasets (must match injection dates).
VERIFICATION_ANCHOR_DATE = date(2026, 6, 30)
CATALOG_V1 = date(2023, 1, 1)
CATALOG_V2 = date(2024, 7, 1)
V2_INCREASE = Decimal("1.15")


@dataclass(frozen=True)
class ProductPlan:
    tier: str
    product_monthly: str
    product_annual: str
    sku: str
    sku_monthly: str
    sku_annual: str
    monthly_price: int
    annual_price: int


def catalog_price(plan: ProductPlan, interval: str, version: str) -> Decimal:
    base = Decimal(plan.monthly_price if interval == "monthly" else plan.annual_price)
    if version == "v2":
        return (base * V2_INCREASE).quantize(Decimal("0.01"))
    return base


def build_product_catalog(rng: random.Random, product_count: int) -> list[ProductPlan]:
    tiers = ["Starter", "Growth", "Professional", "Business", "Enterprise", "Ultimate"]
    base_prices = [49, 99, 199, 399, 699, 999]
    plans: list[ProductPlan] = []
    for index in range(product_count):
        tier = tiers[index % len(tiers)]
        monthly = base_prices[index % len(base_prices)] + rng.randint(0, 20)
        annual = monthly * 10
        slug = tier.lower()
        base_sku = f"SKU-{tier.upper()[:4]}"
        plans.append(
            ProductPlan(
                tier=tier,
                product_monthly=f"prod_{slug}_mo",
                product_annual=f"prod_{slug}_yr",
                sku=base_sku,
                sku_monthly=f"{base_sku}-MO",
                sku_annual=f"{base_sku}-YR",
                monthly_price=monthly,
                annual_price=annual,
            )
        )
    return plans


def build_profile(rng: random.Random, customer_count: int, product_count: int) -> CompanyProfile:
    company_num = rng.randint(1000, 9999)
    return CompanyProfile(
        company_id=f"co_{company_num}",
        name=f"Synthetic Co {company_num}",
        industry=rng.choice(INDUSTRIES),
        arr_target=Decimal(str(rng.randint(100_000, 5_000_000))),
        customer_count=customer_count,
        product_count=product_count,
        billing_platform=rng.choice(BILLING_PLATFORMS),
        crm_platform=rng.choice(CRM_PLATFORMS),
        currency=rng.choice(CURRENCIES),
        locale=rng.choice(LOCALES),
        pricing_strategy=rng.choice(PRICING_STRATEGIES),
        seat_based=rng.random() < 0.5,
    )


def build_baseline_state(
    rng: random.Random,
    customer_count: int,
    product_count: int = 4,
    subscription_multiplier: float = 1.5,
    include_crm: bool = True,
) -> CompanyState:
    profile = build_profile(rng, customer_count, product_count)
    plans = build_product_catalog(rng, product_count)
    state = CompanyState(profile=profile)

    for index in range(1, customer_count + 1):
        customer_id = f"cust_{index:05d}"
        state.customers.append(
            {
                "customer_id": customer_id,
                "name": f"{profile.name} Customer {index:05d} ({profile.industry})",
                "crm_id": f"crm_{index:05d}",
            }
        )
        if include_crm and profile.crm_platform != "none":
            state.crm_accounts.append(
                {
                    "account_id": f"acct_{index:05d}",
                    "customer_id": customer_id,
                    "name": f"Account {index:05d}",
                    "seat_count": rng.randint(1, 50),
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

    for plan in plans:
        for interval, product_id, sku in (
            ("monthly", plan.product_monthly, plan.sku_monthly),
            ("annual", plan.product_annual, plan.sku_annual),
        ):
            for version, effective in (("v1", CATALOG_V1), ("v2", CATALOG_V2)):
                state.price_catalog.append(
                    {
                        "product_id": product_id,
                        "sku": sku,
                        "version": version,
                        "effective_date": effective.isoformat(),
                        "list_price": money(catalog_price(plan, interval, version)),
                        "currency": profile.currency,
                        "billing_interval": interval,
                    }
                )

    sub_count = max(customer_count, int(customer_count * subscription_multiplier))
    customer_ids = [c["customer_id"] for c in state.customers]
    invoice_counter = 1
    line_counter = 1

    for sub_index in range(sub_count):
        sub_id = f"sub_{sub_index + 1:05d}"
        customer_id = customer_ids[sub_index % len(customer_ids)]
        plan = plans[sub_index % len(plans)]
        interval = "monthly" if sub_index % 4 != 0 else "annual"
        product_id = plan.product_monthly if interval == "monthly" else plan.product_annual
        line_sku = plan.sku_monthly if interval == "monthly" else plan.sku_annual
        list_price = catalog_price(plan, interval, "v2")
        quantity = rng.randint(1, 25) if profile.seat_based else rng.randint(1, 5)
        offset = int((sub_index / max(sub_count, 1)) * (HISTORY_END - HISTORY_START).days)
        start = HISTORY_START + timedelta(days=offset)
        renewal = add_months(start) if interval == "monthly" else add_years(start)
        status = "active" if rng.random() < 0.9 else rng.choice(["canceled", "trialing"])

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
                "status": status,
                "coupon_id": "",
                "_plan": plan,
                "_end_date": HISTORY_END.isoformat(),
            }
        )

        end = HISTORY_END if status != "canceled" else min(HISTORY_END, start + timedelta(days=rng.randint(90, 400)))
        unit_price = list_price
        schedule = invoice_schedule(start, interval, end)
        for invoice_date in schedule:
            invoice_id = f"inv_{invoice_counter:07d}"
            subtotal = (unit_price * quantity).quantize(Decimal("0.01"))
            total = subtotal
            state.invoices.append(
                {
                    "invoice_id": invoice_id,
                    "customer_id": customer_id,
                    "subscription_id": sub_id,
                    "invoice_number": f"INV-{invoice_counter:07d}",
                    "invoice_date": invoice_date.isoformat(),
                    "period_start": invoice_date.isoformat(),
                    "period_end": (
                        add_months(invoice_date) if interval == "monthly" else add_years(invoice_date)
                    ).isoformat(),
                    "subtotal": money(subtotal),
                    "discount": "0.00",
                    "total": money(total),
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
                    "unit_price": money(unit_price),
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
