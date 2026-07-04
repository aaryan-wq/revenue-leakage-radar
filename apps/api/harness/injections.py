"""Deterministic leakage injection scenarios with ground-truth recording."""

from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from typing import Callable

from harness.company_state import CompanyState
from harness.money import add_months, add_years, money
from harness.types import GroundTruthFinding
from verification.calculator.financial import compute_period_leakage
from verification.financial import compute_leakage
from verification.helpers import annualize_period_loss


def _anchor(state: CompanyState) -> date:
    """Deterministic dataset date, verification mode sets anchor_date on state."""
    return state.anchor_date or date.today()


def _sync_line_items_to_sub_price(state: CompanyState, sub: dict) -> None:
    """Align invoice lines with subscription price so catalog rules do not cascade into invoice_price_mismatch."""
    unit_price = Decimal(sub["price"])
    sub_id = sub["subscription_id"]
    for line_item in state.line_items:
        if line_item.get("subscription_id") != sub_id:
            continue
        if str(line_item.get("is_manual_override", "")).lower() == "true":
            continue
        quantity = int(line_item.get("quantity") or sub.get("quantity") or 1)
        line_item["unit_price"] = money(unit_price)
        extended = (unit_price * quantity).quantize(Decimal("0.01"))
        line_item["extended_price"] = money(extended)

ALL_RULE_IDS = [
    "legacy_pricing",
    "contract_billing_price_divergence",
    "price_catalog_mismatch",
    "grandfathered_pricing",
    "missing_scheduled_increase",
    "renewal_price_drift",
    "manual_price_override",
    "incorrect_seat_price",
    "incorrect_addon_price",
    "expired_discount",
    "discount_stacking",
    "duplicate_discount",
    "permanent_promotional_discount",
    "excessive_discount",
    "discount_wrong_product",
    "invoice_price_mismatch",
    "duplicate_subscription",
    "billing_frequency_mismatch",
    "active_subscription_not_billing",
    "cancelled_subscription_still_billing",
    "missing_expected_invoice",
    "credit_leakage",
    "duplicate_credit",
    "duplicate_customer",
    "currency_mismatch",
    "orphaned_records",
]

Injector = Callable[[CompanyState, random.Random, set[str], set[str]], list[GroundTruthFinding]]


def _active_subs(state: CompanyState) -> list[dict]:
    return [s for s in state.subscriptions if (s.get("status") or "").lower() in ("active", "trialing")]


def _pick_sub(
    state: CompanyState,
    rng: random.Random,
    used: set[str],
    *,
    min_invoices: int = 0,
    used_customers: set[str] | None = None,
) -> dict | None:
    candidates = [
        s
        for s in _active_subs(state)
        if s["subscription_id"] not in used
        and len(state.invoices_for_subscription(s["subscription_id"])) >= min_invoices
        and (used_customers is None or s["customer_id"] not in used_customers)
    ]
    if not candidates:
        return None
    sub = rng.choice(candidates)
    used.add(sub["subscription_id"])
    if used_customers is not None:
        used_customers.add(sub["customer_id"])
    return sub


def _pick_customer(state: CompanyState, rng: random.Random, used_customers: set[str]) -> str | None:
    candidates = [c["customer_id"] for c in state.customers if c["customer_id"] not in used_customers]
    if not candidates:
        return None
    customer_id = rng.choice(candidates)
    used_customers.add(customer_id)
    return customer_id


def _pick_sub_for_crm(
    state: CompanyState,
    rng: random.Random,
    used_subs: set[str],
    used_customers: set[str],
    *,
    min_invoices: int = 0,
) -> dict | None:
    candidates: list[dict] = []
    for customer in state.customers:
        customer_id = customer["customer_id"]
        if customer_id in used_customers:
            continue
        for sub in _active_subs(state):
            if sub["customer_id"] != customer_id:
                continue
            if sub["subscription_id"] in used_subs:
                continue
            if len(state.invoices_for_subscription(sub["subscription_id"])) < min_invoices:
                continue
            candidates.append(sub)
    if not candidates:
        return None
    sub = rng.choice(candidates)
    used_subs.add(sub["subscription_id"])
    used_customers.add(sub["customer_id"])
    state.crm_contracts = [c for c in state.crm_contracts if c.get("customer_id") != sub["customer_id"]]
    return sub


def inject_expired_discount(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=1, used_customers=used_customers)
    if not sub:
        return []
    plan = sub["_plan"]
    interval = sub["billing_interval"]
    sub["status"] = "active"
    sub["_end_date"] = date(2025, 6, 1).isoformat()
    list_price = Decimal(state.latest_catalog(sub["product_id"])["list_price"])
    discounted = (list_price * Decimal("0.80")).quantize(Decimal("0.01"))
    sub["coupon_id"] = "LAUNCH20"
    sub["price"] = money(discounted)
    sub["start_date"] = date(2023, 8, 1).isoformat()
    _sync_line_items_to_sub_price(state, sub)

    evidence_invoice_id = None
    catalog_at_invoice = list_price
    for inv in sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    ):
        inv_date = date.fromisoformat(inv["invoice_date"][:10])
        if inv_date <= date(2024, 3, 31):
            continue
        subtotal = Decimal(inv["subtotal"])
        inv["discount"] = money(subtotal * Decimal("0.20"))
        evidence_invoice_id = inv["invoice_id"]
        cat = state.catalog_for_product(sub["product_id"], inv_date)
        if cat:
            catalog_at_invoice = Decimal(cat["list_price"])
        break

    if not evidence_invoice_id:
        invoice_id = f"inv_exp_{sub['subscription_id']}"
        inv_date = date(2024, 6, 1)
        subtotal = (discounted * int(sub["quantity"])).quantize(Decimal("0.01"))
        discount = (subtotal * Decimal("0.20")).quantize(Decimal("0.01"))
        state.invoices.append(
            {
                "invoice_id": invoice_id,
                "customer_id": sub["customer_id"],
                "subscription_id": sub["subscription_id"],
                "invoice_number": f"EXP-{sub['subscription_id']}",
                "invoice_date": inv_date.isoformat(),
                "period_start": inv_date.isoformat(),
                "period_end": add_months(inv_date).isoformat(),
                "subtotal": money(subtotal),
                "discount": money(discount),
                "total": money(subtotal - discount),
                "currency": sub["currency"],
                "credit_amount": "0.00",
            }
        )
        state.line_items.append(
            {
                "line_item_id": f"li_exp_{sub['subscription_id']}",
                "invoice_id": invoice_id,
                "customer_id": sub["customer_id"],
                "subscription_id": sub["subscription_id"],
                "product_id": sub["product_id"],
                "sku": plan.sku_monthly if interval == "monthly" else plan.sku_annual,
                "quantity": sub["quantity"],
                "unit_price": money(discounted),
                "extended_price": money(subtotal),
                "billing_interval": interval,
                "line_item_date": inv_date.isoformat(),
                "currency": sub["currency"],
                "is_manual_override": "false",
            }
        )
        evidence_invoice_id = invoice_id
        cat = state.catalog_for_product(sub["product_id"], inv_date)
        if cat:
            catalog_at_invoice = Decimal(cat["list_price"])

    monthly, annual = compute_leakage(catalog_at_invoice, discounted, int(sub["quantity"]), interval)
    finding = GroundTruthFinding(
        rule_id="expired_discount",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=evidence_invoice_id,
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
        expected_evidence={"coupon": "LAUNCH20"},
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_legacy_sku_drift(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=1, used_customers=used_customers)
    if not sub:
        return []
    interval = sub["billing_interval"]
    addon_product = f"addon_{sub['product_id']}"
    latest = Decimal(state.latest_catalog(sub["product_id"])["list_price"])
    v1_price = (latest * Decimal("0.85")).quantize(Decimal("0.01"))
    if not state.latest_catalog(addon_product):
        state.price_catalog.append(
            {
                "product_id": addon_product,
                "sku": addon_product,
                "version": "v2",
                "effective_date": date(2024, 7, 1).isoformat(),
                "list_price": money(latest),
                "currency": state.profile.currency,
                "billing_interval": interval,
            }
        )
    invoice = state.invoices_for_subscription(sub["subscription_id"])[-1]
    line = {
        "line_item_id": f"li_addon_{sub['subscription_id']}",
        "invoice_id": invoice["invoice_id"],
        "customer_id": sub["customer_id"],
        "subscription_id": sub["subscription_id"],
        "product_id": addon_product,
        "sku": addon_product,
        "quantity": "1",
        "unit_price": money(v1_price),
        "extended_price": money(v1_price),
        "billing_interval": interval,
        "line_item_date": invoice["invoice_date"],
        "currency": state.profile.currency,
        "is_manual_override": "false",
    }
    state.line_items.append(line)
    monthly, annual = compute_leakage(latest, v1_price, 1, interval)
    finding = GroundTruthFinding(
        rule_id="incorrect_addon_price",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_legacy_pricing_pre_catalog(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    start = date(2022, 6, 1)
    sub["start_date"] = start.isoformat()
    sub["status"] = "active"
    latest = Decimal(state.latest_catalog(sub["product_id"])["list_price"])
    underpriced = (latest * Decimal("0.85")).quantize(Decimal("0.01"))
    sub["price"] = money(underpriced)
    _sync_line_items_to_sub_price(state, sub)
    monthly, annual = compute_leakage(latest, underpriced, int(sub["quantity"]), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="legacy_pricing",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_renewal_price_drift(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=2, used_customers=used_customers)
    if not sub:
        return []
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if len(invoices) < 2:
        return []
    prior = invoices[-2]
    renewal = invoices[-1]
    prior_line_items = state.line_items_for_invoice(prior["invoice_id"])
    renewal_line_items = state.line_items_for_invoice(renewal["invoice_id"])
    qty = int(sub.get("quantity") or 1)
    if prior_line_items and renewal_line_items:
        prior_unit = Decimal(prior_line_items[0]["unit_price"])
        reduced_unit = (prior_unit * Decimal("0.90")).quantize(Decimal("0.01"))
        renewal_line_items[0]["unit_price"] = money(reduced_unit)
        expected_unit = prior_unit
        actual_unit = reduced_unit
    else:
        prior_total = Decimal(prior["total"])
        reduced = (prior_total * Decimal("0.90")).quantize(Decimal("0.01"))
        renewal["total"] = money(reduced)
        expected_unit = (prior_total / Decimal(str(qty))).quantize(Decimal("0.0001"))
        actual_unit = (reduced / Decimal(str(qty))).quantize(Decimal("0.0001"))
    monthly, annual = compute_leakage(expected_unit, actual_unit, qty, sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="renewal_price_drift",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=renewal["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_duplicate_discount(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    sub["coupon_id"] = "PARTNER15"
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if not invoices:
        return []
    invoice = invoices[-1]
    base = Decimal(invoice["subtotal"])
    invoice["discount"] = money(base * Decimal("0.10"))
    discount = Decimal(invoice["discount"])
    stacked_loss = min(discount, base * Decimal("0.1"))
    monthly, annual, _ = compute_period_leakage(stacked_loss, Decimal("0"), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="discount_stacking",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_price_catalog_mismatch(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = None
    for _ in range(10):
        candidate = _pick_sub(state, rng, used, used_customers=used_customers)
        if not candidate:
            return []
        if not candidate.get("coupon_id"):
            sub = candidate
            break
    if sub is None:
        return []
    sub["coupon_id"] = ""
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if not invoices:
        return []
    invoice = invoices[-1]
    line_items = state.line_items_for_invoice(invoice["invoice_id"])
    if not line_items:
        return []
    li = line_items[0]
    inv_date = date.fromisoformat(invoice["invoice_date"][:10])
    catalog_row = state.catalog_for_product(sub["product_id"], inv_date)
    catalog_price = Decimal(
        catalog_row["list_price"] if catalog_row else state.latest_catalog(sub["product_id"])["list_price"]
    )
    under = (catalog_price * Decimal("0.88")).quantize(Decimal("0.01"))
    sub["price"] = money(under)
    _sync_line_items_to_sub_price(state, sub)
    monthly, annual = compute_leakage(catalog_price, under, int(sub.get("quantity") or 1), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="price_catalog_mismatch",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_grandfathered(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    latest = Decimal(state.latest_catalog(sub["product_id"])["list_price"])
    under = (latest * Decimal("0.85")).quantize(Decimal("0.01"))
    sub["price"] = money(under)
    sub["start_date"] = date(2022, 1, 1).isoformat()
    sub["status"] = "active"
    _sync_line_items_to_sub_price(state, sub)
    monthly, annual = compute_leakage(latest, under, int(sub["quantity"]), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="grandfathered_pricing",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_missing_scheduled_increase(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub_for_crm(state, rng, used, used_customers)
    if not sub:
        return []
    latest = Decimal(state.latest_catalog(sub["product_id"])["list_price"])
    under = (latest * Decimal("0.90")).quantize(Decimal("0.01"))
    sub["price"] = money(under)
    sub["status"] = "active"
    _sync_line_items_to_sub_price(state, sub)
    customer_id = sub["customer_id"]
    account = next((a for a in state.crm_accounts if a["customer_id"] == customer_id), None)
    if not account:
        account = {
            "account_id": f"acct_{customer_id}",
            "customer_id": customer_id,
            "name": f"Account {customer_id}",
            "seat_count": int(sub["quantity"]),
        }
        state.crm_accounts.append(account)
    state.crm_contracts.append(
        {
            "contract_id": f"ctr_inc_{sub['subscription_id']}",
            "account_id": account["account_id"],
            "customer_id": customer_id,
            "contract_price": money(latest),
            "price_increase_date": date(2024, 1, 1).isoformat(),
            "expected_renewal_price": money(latest),
            "start_date": date(2023, 1, 1).isoformat(),
            "end_date": date(2026, 1, 1).isoformat(),
            "seat_count": str(sub["quantity"]),
        }
    )
    monthly, annual = compute_leakage(latest, under, int(sub["quantity"]), sub["billing_interval"])
    severity = "high"

    finding = GroundTruthFinding(
        rule_id="missing_scheduled_increase",
        customer_id=customer_id,
        subscription_id=sub["subscription_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity=severity,
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_invoice_subscription_mismatch(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    sub_price = Decimal(sub["price"])
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if not invoices:
        return []
    invoice = invoices[-1]
    line_items = state.line_items_for_invoice(invoice["invoice_id"])
    if not line_items:
        return []
    under = (sub_price * Decimal("0.88")).quantize(Decimal("0.01"))
    line_items[0]["unit_price"] = money(under)
    line_items[0]["quantity"] = sub["quantity"]
    monthly, annual = compute_leakage(sub_price, under, int(sub["quantity"]), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="invoice_price_mismatch",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_duplicate_active_subscriptions(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    customer_id = _pick_customer(state, rng, used_customers)
    if not customer_id:
        return []
    used_customers.add(customer_id)
    plan = state.subscriptions[0]["_plan"]
    product_id = plan.product_monthly
    price = Decimal(state.latest_catalog(product_id)["list_price"])
    for sub in state.subscriptions:
        if (
            sub["customer_id"] == customer_id
            and sub.get("product_id") == product_id
            and (sub.get("status") or "").lower() in ("active", "trialing")
        ):
            sub["status"] = "cancelled"
    for index in range(2):
        sub_id = f"sub_dup_{customer_id}_{index}"
        state.subscriptions.append(
            {
                "subscription_id": sub_id,
                "customer_id": customer_id,
                "product_id": product_id,
                "plan": plan.tier,
                "quantity": 1,
                "billing_interval": "monthly",
                "price": money(price),
                "currency": state.profile.currency,
                "start_date": date(2024, 1, 1).isoformat(),
                "renewal_date": date(2024, 2, 1).isoformat(),
                "status": "active",
                "coupon_id": "",
                "_plan": plan,
                "_end_date": date(2025, 6, 1).isoformat(),
            }
        )
    monthly_loss, annual_loss = compute_leakage(price, Decimal("0"), 1, "monthly")
    finding = GroundTruthFinding(
        rule_id="duplicate_subscription",
        customer_id=customer_id,
        subscription_id=f"sub_dup_{customer_id}_1",
        expected_monthly_leakage=monthly_loss,
        expected_annual_leakage=annual_loss,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_billing_frequency_mismatch(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if not invoices:
        return []
    invoice = invoices[-1]
    sub["billing_interval"] = "monthly"
    period_start = date.fromisoformat(invoice["period_start"])
    invoice["period_end"] = (period_start + timedelta(days=60)).isoformat()
    finding = GroundTruthFinding(
        rule_id="billing_frequency_mismatch",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=Decimal("0"),
        expected_annual_leakage=Decimal("0"),
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_currency_inconsistency(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    alt_currency = "EUR" if sub["currency"] == "USD" else "USD"
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if not invoices:
        return []
    invoice = invoices[-1]
    invoice["currency"] = alt_currency
    finding = GroundTruthFinding(
        rule_id="currency_mismatch",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=Decimal("0"),
        expected_annual_leakage=Decimal("0"),
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_credit_leakage(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    customer_id = _pick_customer(state, rng, used_customers)
    if not customer_id:
        return []
    invoice_id = f"inv_credit_{customer_id}"
    subtotal = Decimal("1000.00")
    credit = (subtotal * Decimal("1.5")).quantize(Decimal("0.01"))
    state.invoices.append(
        {
            "invoice_id": invoice_id,
            "customer_id": customer_id,
            "subscription_id": None,
            "invoice_number": f"CR-{customer_id}",
            "invoice_date": _anchor(state).isoformat(),
            "period_start": _anchor(state).isoformat(),
            "period_end": add_months(_anchor(state)).isoformat(),
            "subtotal": money(subtotal),
            "discount": "0.00",
            "total": money(Decimal("0")),
            "currency": state.profile.currency,
            "credit_amount": money(credit),
        }
    )
    monthly = (credit - subtotal).quantize(Decimal("0.0001"))
    annual = Decimal("0")
    finding = GroundTruthFinding(
        rule_id="credit_leakage",
        customer_id=customer_id,
        invoice_id=invoice_id,
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_manual_override(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, used_customers=used_customers)
    if not sub:
        return []
    invoices = sorted(
        state.invoices_for_subscription(sub["subscription_id"]),
        key=lambda row: row.get("invoice_date") or "",
    )
    if not invoices:
        return []
    invoice = invoices[-1]
    line_items = state.line_items_for_invoice(invoice["invoice_id"])
    if not line_items:
        return []
    li = line_items[0]
    inv_date = date.fromisoformat(invoice["invoice_date"][:10])
    catalog_row = state.catalog_for_product(sub["product_id"], inv_date)
    catalog_price = Decimal(catalog_row["list_price"]) if catalog_row else Decimal(state.latest_catalog(sub["product_id"])["list_price"])
    under = (catalog_price * Decimal("0.75")).quantize(Decimal("0.01"))
    li["unit_price"] = money(under)
    li["is_manual_override"] = "true"
    interval = li.get("billing_interval") or sub.get("billing_interval") or "monthly"
    monthly, annual = compute_leakage(catalog_price, under, int(li["quantity"]), interval)
    finding = GroundTruthFinding(
        rule_id="manual_price_override",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_discount_past_contract_end(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub_for_crm(state, rng, used, used_customers)
    if not sub:
        return []
    customer_id = sub["customer_id"]
    account = next((a for a in state.crm_accounts if a["customer_id"] == customer_id), None)
    if not account:
        state.crm_accounts.append(
            {
                "account_id": f"acct_{customer_id}",
                "customer_id": customer_id,
                "name": f"Account {customer_id}",
                "seat_count": 10,
            }
        )
        account = state.crm_accounts[-1]
    sub["coupon_id"] = "REFER10"
    contract_id = f"ctr_{customer_id}"
    state.crm_contracts.append(
        {
            "contract_id": contract_id,
            "account_id": account["account_id"],
            "customer_id": customer_id,
            "contract_price": sub["price"],
            "price_increase_date": "",
            "expected_renewal_price": sub["price"],
            "start_date": date(2023, 1, 1).isoformat(),
            "end_date": date(2024, 1, 1).isoformat(),
            "seat_count": "10",
        }
    )
    finding = GroundTruthFinding(
        rule_id="permanent_promotional_discount",
        customer_id=customer_id,
        subscription_id=sub["subscription_id"],
        expected_monthly_leakage=Decimal("0"),
        expected_annual_leakage=Decimal("0"),
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_seat_underbilling(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub_for_crm(state, rng, used, used_customers)
    if not sub:
        return []
    customer_id = sub["customer_id"]
    account = next((a for a in state.crm_accounts if a["customer_id"] == customer_id), None)
    if not account:
        state.crm_accounts.append(
            {
                "account_id": f"acct_{customer_id}",
                "customer_id": customer_id,
                "name": f"Account {customer_id}",
                "seat_count": 50,
            }
        )
        account = state.crm_accounts[-1]
    else:
        account["seat_count"] = int(sub["quantity"]) + rng.randint(5, 20)
    sub["quantity"] = max(1, int(account["seat_count"]) - 10)
    extra_seats = int(account["seat_count"]) - int(sub["quantity"])
    unit_price = Decimal(sub["price"])
    monthly, annual = compute_leakage(unit_price, Decimal("0"), extra_seats, sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="incorrect_seat_price",
        customer_id=customer_id,
        subscription_id=sub["subscription_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_contract_billing_divergence(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub_for_crm(state, rng, used, used_customers)
    if not sub:
        return []
    customer_id = sub["customer_id"]
    account = next((a for a in state.crm_accounts if a["customer_id"] == customer_id), None)
    if not account:
        state.crm_accounts.append(
            {
                "account_id": f"acct_{customer_id}",
                "customer_id": customer_id,
                "name": f"Account {customer_id}",
                "seat_count": 10,
            }
        )
        account = state.crm_accounts[-1]
    contract_price = (Decimal(sub["price"]) * Decimal("1.20")).quantize(Decimal("0.01"))
    state.crm_contracts.append(
        {
            "contract_id": f"ctr_{sub['subscription_id']}",
            "account_id": account["account_id"],
            "customer_id": customer_id,
            "contract_price": money(contract_price),
            "price_increase_date": "",
            "expected_renewal_price": money(contract_price),
            "start_date": date(2024, 1, 1).isoformat(),
            "end_date": date(2026, 1, 1).isoformat(),
            "seat_count": str(sub["quantity"]),
        }
    )
    monthly, annual = compute_leakage(contract_price, Decimal(sub["price"]), int(sub["quantity"]), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="contract_billing_price_divergence",
        customer_id=customer_id,
        subscription_id=sub["subscription_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_underpriced_renewal_vs_contract(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub_for_crm(state, rng, used, used_customers, min_invoices=1)
    if not sub:
        return []
    customer_id = sub["customer_id"]
    account = next((a for a in state.crm_accounts if a["customer_id"] == customer_id), None)
    if not account:
        state.crm_accounts.append(
            {
                "account_id": f"acct_{customer_id}",
                "customer_id": customer_id,
                "name": f"Account {customer_id}",
                "seat_count": 10,
            }
        )
        account = state.crm_accounts[-1]
    invoices = state.invoices_for_subscription(sub["subscription_id"])
    if not invoices:
        return []
    renewal = invoices[-1]
    renewal_line_items = state.line_items_for_invoice(renewal["invoice_id"])
    qty = int(sub.get("quantity") or 1)
    if renewal_line_items:
        renewal_unit = Decimal(renewal_line_items[0]["unit_price"])
        expected_renewal = (renewal_unit * Decimal("1.25")).quantize(Decimal("0.01"))
        actual_unit = renewal_unit
    else:
        renewal_total = Decimal(renewal["total"])
        expected_renewal = (renewal_total * Decimal("1.25")).quantize(Decimal("0.01"))
        actual_unit = (renewal_total / Decimal(str(qty))).quantize(Decimal("0.0001"))
        expected_renewal = (expected_renewal / Decimal(str(qty))).quantize(Decimal("0.0001"))
    state.crm_contracts.append(
        {
            "contract_id": f"ctr_ren_{sub['subscription_id']}",
            "account_id": account["account_id"],
            "customer_id": customer_id,
            "contract_price": sub["price"],
            "price_increase_date": "",
            "expected_renewal_price": money(expected_renewal),
            "start_date": date(2024, 1, 1).isoformat(),
            "end_date": date(2026, 1, 1).isoformat(),
            "seat_count": str(sub["quantity"]),
        }
    )
    monthly, annual = compute_leakage(expected_renewal, actual_unit, qty, sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="renewal_price_drift",
        customer_id=customer_id,
        subscription_id=sub["subscription_id"],
        invoice_id=renewal["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_free_plan(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    customer_id = _pick_customer(state, rng, used_customers)
    if not customer_id:
        return []
    plan = state.subscriptions[0]["_plan"]
    sub_id = f"sub_free_{customer_id}"
    catalog_price = Decimal(state.latest_catalog(plan.product_monthly)["list_price"])
    state.subscriptions.append(
        {
            "subscription_id": sub_id,
            "customer_id": customer_id,
            "product_id": plan.product_monthly,
            "plan": "Growth",
            "quantity": 1,
            "billing_interval": "monthly",
            "price": money(catalog_price),
            "currency": state.profile.currency,
            "start_date": date(2023, 1, 1).isoformat(),
            "renewal_date": date(2023, 2, 1).isoformat(),
            "status": "active",
            "coupon_id": "",
            "_plan": plan,
            "_end_date": date(2025, 6, 1).isoformat(),
        }
    )
    finding = GroundTruthFinding(
        rule_id="active_subscription_not_billing",
        customer_id=customer_id,
        subscription_id=sub_id,
        expected_monthly_leakage=catalog_price,
        expected_annual_leakage=catalog_price * Decimal("12"),
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_discount_abuse(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    customer_id = _pick_customer(state, rng, used_customers)
    if not customer_id:
        return []
    used_customers.add(customer_id)
    sub = next((s for s in state.subscriptions if s["customer_id"] == customer_id), state.subscriptions[0])
    used.add(sub["subscription_id"])
    discounted_invoices: list[dict] = []
    for index in range(4):
        invoice_id = f"inv_abuse_{customer_id}_{index}"
        amount = Decimal("100.00")
        discount = Decimal("10.00")
        inv_date = _anchor(state) - timedelta(days=30 * (index + 1))
        state.invoices.append(
            {
                "invoice_id": invoice_id,
                "customer_id": customer_id,
                "subscription_id": sub["subscription_id"],
                "invoice_number": f"ABUSE-{index}",
                "invoice_date": inv_date.isoformat(),
                "period_start": inv_date.isoformat(),
                "period_end": add_months(inv_date).isoformat(),
                "subtotal": money(amount),
                "discount": money(discount),
                "total": money(amount - discount),
                "currency": state.profile.currency,
                "credit_amount": "0.00",
            }
        )
        discounted_invoices.append(state.invoices[-1])
    sorted_invoices = sorted(discounted_invoices, key=lambda inv: inv["invoice_date"])
    total_discount = sum(Decimal(inv["discount"]) for inv in sorted_invoices)
    monthly, annual, _ = compute_period_leakage(
        total_discount / Decimal("12"),
        Decimal("0"),
        "monthly",
    )
    finding = GroundTruthFinding(
        rule_id="excessive_discount",
        customer_id=customer_id,
        subscription_id=sub["subscription_id"],
        invoice_id=sorted_invoices[0]["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_duplicate_discount_rule(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=2, used_customers=used_customers)
    if not sub:
        return []
    sub["coupon_id"] = "DUP10"
    invoices = state.invoices_for_subscription(sub["subscription_id"])
    if len(invoices) < 2:
        return []
    for inv in invoices[-2:]:
        subtotal = Decimal(inv.get("subtotal") or "100")
        inv["discount"] = money(subtotal * Decimal("0.10"))
    duplicate_amount = Decimal(invoices[-1]["discount"])
    monthly, annual = annualize_period_loss(duplicate_amount, sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="duplicate_discount",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoices[-1]["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_cancelled_still_billing(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=1, used_customers=used_customers)
    if not sub:
        return []
    sub["status"] = "cancelled"
    sub["renewal_date"] = date(2024, 1, 1).isoformat()
    invoice = state.invoices_for_subscription(sub["subscription_id"])[-1]
    invoice["invoice_date"] = date(2024, 6, 1).isoformat()
    invoice["total"] = money(Decimal(sub["price"]) * int(sub.get("quantity") or 1))
    total = Decimal(invoice["total"])
    monthly, annual = annualize_period_loss(total, sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="cancelled_subscription_still_billing",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_missing_expected_invoice(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=1, used_customers=used_customers)
    if not sub:
        return []
    invoice = state.invoices_for_subscription(sub["subscription_id"])[-1]
    invoice["period_end"] = date(2023, 1, 1).isoformat()
    monthly, annual = compute_leakage(Decimal(sub["price"]), Decimal("0"), int(sub.get("quantity") or 1), sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="missing_expected_invoice",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="medium",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_duplicate_credit(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    customer_id = _pick_customer(state, rng, used_customers)
    if not customer_id:
        return []
    credit = Decimal("50.00")
    for index in range(2):
        state.invoices.append(
            {
                "invoice_id": f"inv_dup_credit_{customer_id}_{index}",
                "customer_id": customer_id,
                "subscription_id": None,
                "invoice_number": f"DUP-CR-{index}",
                "invoice_date": _anchor(state).isoformat(),
                "period_start": _anchor(state).isoformat(),
                "period_end": add_months(_anchor(state)).isoformat(),
                "subtotal": money(credit),
                "discount": "0.00",
                "total": money(Decimal("0")),
                "currency": state.profile.currency,
                "credit_amount": money(credit),
            }
        )
    monthly, annual = annualize_period_loss(credit, "monthly")
    finding = GroundTruthFinding(
        rule_id="duplicate_credit",
        customer_id=customer_id,
        subscription_id=None,
        invoice_id=state.invoices[-1]["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_duplicate_customer(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    if len(state.customers) < 2:
        return []
    base = rng.choice(state.customers)
    duplicate = next(c for c in state.customers if c["customer_id"] != base["customer_id"])
    duplicate["name"] = base["name"]
    finding = GroundTruthFinding(
        rule_id="duplicate_customer",
        customer_id=base["customer_id"],
        subscription_id=None,
        invoice_id=None,
        expected_monthly_leakage=Decimal("0"),
        expected_annual_leakage=Decimal("0"),
        expected_severity="low",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_orphaned_records(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    orphan_invoice_id = "00000000-0000-4000-8000-000000000099"
    state.line_items.append(
        {
            "line_item_id": "orphan_li_001",
            "invoice_id": orphan_invoice_id,
            "customer_id": state.customers[0]["customer_id"] if state.customers else "cust_orphan",
            "subscription_id": None,
            "product_id": "prod_orphan",
            "sku": "ORPHAN",
            "quantity": "1",
            "unit_price": "99.00",
            "extended_price": "99.00",
            "billing_interval": "monthly",
            "line_item_date": _anchor(state).isoformat(),
            "currency": state.profile.currency,
            "is_manual_override": "false",
        }
    )
    finding = GroundTruthFinding(
        rule_id="orphaned_records",
        customer_id=state.customers[0]["customer_id"] if state.customers else None,
        subscription_id=None,
        invoice_id=None,
        expected_monthly_leakage=Decimal("0"),
        expected_annual_leakage=Decimal("0"),
        expected_severity="low",
    )
    state.append_ground_truth(finding)
    return [finding]


def inject_discount_wrong_product(state: CompanyState, rng: random.Random, used: set[str], used_customers: set[str]) -> list[GroundTruthFinding]:
    sub = _pick_sub(state, rng, used, min_invoices=1, used_customers=used_customers)
    if not sub:
        return []
    sub["coupon_id"] = "PROD10"
    invoice = state.invoices_for_subscription(sub["subscription_id"])[-1]
    invoice["discount"] = money(Decimal(invoice.get("subtotal") or "100") * Decimal("0.10"))
    wrong_product = f"addon_{sub['product_id']}"
    if not state.latest_catalog(wrong_product):
        state.price_catalog.append(
            {
                "product_id": wrong_product,
                "sku": wrong_product,
                "version": "v1",
                "effective_date": date(2023, 1, 1).isoformat(),
                "list_price": money(Decimal(sub["price"])),
                "currency": state.profile.currency,
                "billing_interval": sub["billing_interval"],
            }
        )
    line = {
        "line_item_id": f"li_wrong_{sub['subscription_id']}",
        "invoice_id": invoice["invoice_id"],
        "customer_id": sub["customer_id"],
        "subscription_id": sub["subscription_id"],
        "product_id": wrong_product,
        "sku": wrong_product,
        "quantity": "1",
        "unit_price": money(Decimal(sub["price"]) * Decimal("0.50")),
        "extended_price": money(Decimal(sub["price"]) * Decimal("0.50")),
        "billing_interval": sub["billing_interval"],
        "line_item_date": invoice["invoice_date"],
        "currency": state.profile.currency,
        "is_manual_override": "false",
    }
    state.line_items.append(line)
    catalog_price = Decimal(state.latest_catalog(wrong_product)["list_price"]) if state.latest_catalog(wrong_product) else Decimal("100")
    actual = Decimal(line["unit_price"])
    monthly, annual = compute_leakage(catalog_price, actual, 1, sub["billing_interval"])
    finding = GroundTruthFinding(
        rule_id="discount_wrong_product",
        customer_id=sub["customer_id"],
        subscription_id=sub["subscription_id"],
        invoice_id=invoice["invoice_id"],
        expected_monthly_leakage=monthly,
        expected_annual_leakage=annual,
        expected_severity="high",
    )
    state.append_ground_truth(finding)
    return [finding]


INJECTORS: dict[str, Injector] = {
    "legacy_pricing": inject_legacy_pricing_pre_catalog,
    "contract_billing_price_divergence": inject_contract_billing_divergence,
    "price_catalog_mismatch": inject_price_catalog_mismatch,
    "grandfathered_pricing": inject_grandfathered,
    "missing_scheduled_increase": inject_missing_scheduled_increase,
    "renewal_price_drift": inject_renewal_price_drift,
    "manual_price_override": inject_manual_override,
    "incorrect_seat_price": inject_seat_underbilling,
    "incorrect_addon_price": inject_legacy_sku_drift,
    "expired_discount": inject_expired_discount,
    "discount_stacking": inject_duplicate_discount,
    "duplicate_discount": inject_duplicate_discount_rule,
    "permanent_promotional_discount": inject_discount_past_contract_end,
    "excessive_discount": inject_discount_abuse,
    "discount_wrong_product": inject_discount_wrong_product,
    "invoice_price_mismatch": inject_invoice_subscription_mismatch,
    "duplicate_subscription": inject_duplicate_active_subscriptions,
    "billing_frequency_mismatch": inject_billing_frequency_mismatch,
    "active_subscription_not_billing": inject_free_plan,
    "cancelled_subscription_still_billing": inject_cancelled_still_billing,
    "missing_expected_invoice": inject_missing_expected_invoice,
    "credit_leakage": inject_credit_leakage,
    "duplicate_credit": inject_duplicate_credit,
    "duplicate_customer": inject_duplicate_customer,
    "currency_mismatch": inject_currency_inconsistency,
    "orphaned_records": inject_orphaned_records,
}


def apply_injections(
    state: CompanyState,
    rng: random.Random,
    rule_ids: list[str] | None = None,
) -> list[GroundTruthFinding]:
    targets = rule_ids or list(INJECTORS.keys())
    used_subs: set[str] = set()
    used_customers: set[str] = set()
    findings: list[GroundTruthFinding] = []
    for rule_id in targets:
        injector = INJECTORS.get(rule_id)
        if injector:
            findings.extend(injector(state, rng, used_subs, used_customers))
    return findings
