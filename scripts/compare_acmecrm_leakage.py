#!/usr/bin/env python3
"""Compare AI-style historical leakage vs deterministic engine on AcmeCRM."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from verification.attribution import attribute_findings, sum_primary_recoverable_arr, sum_secondary_excluded_arr
from verification.registry import get_all_rules

DATA = ROOT / "testdata" / "acmecrm"


def load_csv(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def monthly_factor(interval: str) -> Decimal:
    interval = (interval or "monthly").lower()
    if interval in ("annual", "yearly", "year"):
        return Decimal("1") / Decimal("12")
    return Decimal("1")


def build_context():
    import uuid
    from datetime import timezone

    from models import Coupon, Invoice, InvoiceLineItem, PriceCatalog, Subscription
    from verification.context import AuditContext

    company_id = uuid.uuid4()
    audit_id = uuid.uuid4()
    id_map: dict[str, dict[str, uuid.UUID]] = {"customer": {}, "subscription": {}, "invoice": {}}

    def parse_date(value: str | None):
        if not value:
            return None
        return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)

    def parse_decimal(value: str | None) -> Decimal | None:
        if value is None or value == "":
            return None
        return Decimal(str(value))

    for row in load_csv("customers.csv"):
        id_map["customer"][row["customer_id"]] = uuid.uuid4()

    subscriptions: list[Subscription] = []
    for row in load_csv("subscriptions.csv"):
        sub_uuid = uuid.uuid4()
        id_map["subscription"][row["subscription_id"]] = sub_uuid
        subscriptions.append(
            Subscription(
                id=sub_uuid,
                customer_id=id_map["customer"][row["customer_id"]],
                external_subscription_id=row["subscription_id"],
                product_id=row["product_id"],
                plan=row["plan"],
                quantity=int(row["quantity"]),
                billing_interval=row["billing_interval"],
                price=parse_decimal(row["price"]),
                currency=row["currency"],
                start_date=parse_date(row["start_date"]),
                renewal_date=parse_date(row["renewal_date"]),
                status=row["status"],
                coupon_id=row.get("coupon_id") or None,
            )
        )

    invoices: list[Invoice] = []
    for row in load_csv("invoices.csv"):
        inv_uuid = uuid.uuid4()
        id_map["invoice"][row["invoice_id"]] = inv_uuid
        sub_key = row.get("subscription_id") or ""
        invoices.append(
            Invoice(
                id=inv_uuid,
                customer_id=id_map["customer"][row["customer_id"]],
                subscription_id=id_map["subscription"].get(sub_key),
                invoice_number=row["invoice_number"],
                invoice_date=parse_date(row["invoice_date"]),
                period_start=parse_date(row.get("period_start")),
                period_end=parse_date(row.get("period_end")),
                subtotal=parse_decimal(row.get("subtotal")),
                discount=parse_decimal(row.get("discount")),
                total=parse_decimal(row.get("total")),
                currency=row["currency"],
            )
        )

    line_items: list[InvoiceLineItem] = []
    for row in load_csv("invoice_line_items.csv"):
        inv_key = row["invoice_id"]
        sub_key = row.get("subscription_id") or ""
        line_items.append(
            InvoiceLineItem(
                id=uuid.uuid4(),
                invoice_id=id_map["invoice"][inv_key],
                customer_id=id_map["customer"].get(row.get("customer_id") or ""),
                subscription_id=id_map["subscription"].get(sub_key),
                product_id=row["product_id"],
                sku=row.get("sku"),
                quantity=int(row["quantity"]),
                unit_price=parse_decimal(row["unit_price"]),
                extended_price=parse_decimal(row.get("extended_price")),
                billing_interval=row.get("billing_interval"),
                line_item_date=parse_date(row.get("line_item_date")),
                currency=row.get("currency"),
            )
        )

    coupons: list[Coupon] = []
    for row in load_csv("coupons.csv"):
        coupons.append(
            Coupon(
                id=uuid.uuid4(),
                company_id=company_id,
                code=row["code"],
                discount_type=row.get("discount_type"),
                discount_value=parse_decimal(row.get("discount_value")),
                expires_at=parse_date(row.get("expires_at")),
                active=row.get("active", "").lower() == "true",
            )
        )

    price_catalog: list[PriceCatalog] = []
    for row in load_csv("price_catalog.csv"):
        price_catalog.append(
            PriceCatalog(
                id=uuid.uuid4(),
                company_id=company_id,
                product_id=row["product_id"],
                sku=row.get("sku"),
                version=row.get("version"),
                effective_date=parse_date(row.get("effective_date")),
                list_price=parse_decimal(row["list_price"]),
                currency=row.get("currency"),
                billing_interval=row.get("billing_interval"),
            )
        )

    return AuditContext(
        audit_id=audit_id,
        company_id=company_id,
        subscriptions=subscriptions,
        invoices=invoices,
        line_items=line_items,
        coupons=coupons,
        price_catalog=price_catalog,
        has_crm=False,
    )


def ai_style_metrics() -> dict[str, Decimal]:
    invoices = load_csv("invoices.csv")
    subs = {r["subscription_id"]: r for r in load_csv("subscriptions.csv")}
    catalog_rows = load_csv("price_catalog.csv")
    line_items = load_csv("invoice_line_items.csv")

    total_revenue = sum(Decimal(r["total"]) for r in invoices)
    total_discounts = sum(Decimal(r.get("discount") or 0) for r in invoices)

    launch_exp = datetime.fromisoformat("2024-03-31")
    expired_launch_discount = Decimal("0")
    for inv in invoices:
        discount = Decimal(inv.get("discount") or 0)
        if discount <= 0:
            continue
        sub = subs.get(inv.get("subscription_id") or "")
        if sub and sub.get("coupon_id") == "LAUNCH20":
            inv_date = datetime.fromisoformat(inv["invoice_date"])
            if inv_date > launch_exp:
                expired_launch_discount += discount

    latest_catalog: dict[str, dict[str, str]] = {}
    for row in catalog_rows:
        pid = row["product_id"]
        if pid not in latest_catalog or row["effective_date"] > latest_catalog[pid]["effective_date"]:
            latest_catalog[pid] = row

    trial_leakage = Decimal("0")
    for sub in subs.values():
        if sub["status"] != "trialing":
            continue
        cat = latest_catalog.get(sub["product_id"])
        if not cat:
            continue
        price = Decimal(cat["list_price"])
        qty = int(sub["quantity"])
        factor = monthly_factor(sub["billing_interval"])
        trial_leakage += price * qty * factor * Decimal("12")

    cat_v2 = {row["product_id"]: Decimal(row["list_price"]) for row in catalog_rows if row["version"] == "v2"}
    hidden = Decimal("0")
    for li in line_items:
        cat_price = cat_v2.get(li["product_id"])
        if not cat_price:
            continue
        unit = Decimal(li["unit_price"])
        if unit < cat_price:
            qty = int(li["quantity"])
            factor = monthly_factor(li["billing_interval"])
            hidden += (cat_price - unit) * qty * factor

    return {
        "total_revenue": total_revenue,
        "explicit_discounts": total_discounts,
        "expired_launch20_discounts": expired_launch_discount,
        "hidden_pricing_leakage": hidden,
        "trial_leakage": trial_leakage,
        "ai_total_leakage": total_discounts + hidden + trial_leakage,
    }


def engine_metrics(ctx):
    by_rule: dict[str, dict[str, Decimal | int]] = defaultdict(lambda: {"count": 0, "arr": Decimal("0")})
    all_findings = []
    for rule in get_all_rules():
        if not rule.evaluate:
            continue
        findings = rule.evaluate(ctx)
        for finding in findings:
            by_rule[finding.rule_id]["count"] += 1
            by_rule[finding.rule_id]["arr"] += finding.estimated_arr_loss
        all_findings.extend(findings)

    unique_subs = len({f.subscription_id for f in all_findings if f.subscription_id})
    return {
        "finding_count": len(all_findings),
        "unique_subscriptions": unique_subs,
        "total_recoverable_arr": sum((f.estimated_arr_loss for f in all_findings), Decimal("0")),
        "by_rule": dict(by_rule),
    }



def main() -> None:
    ai = ai_style_metrics()
    ctx = build_context()
    engine = engine_metrics(ctx)

    all_findings = []
    for rule in get_all_rules():
        if rule.evaluate:
            all_findings.extend(rule.evaluate(ctx))
    attributed = attribute_findings(all_findings)
    raw_arr = sum((f.estimated_arr_loss for f in all_findings), Decimal("0"))
    primary_arr = sum_primary_recoverable_arr(attributed)
    secondary_arr = sum_secondary_excluded_arr(attributed)

    print("AcmeCRM leakage comparison")
    print("=" * 60)
    print("\nAI-style (historical / cumulative):")
    for key, value in ai.items():
        print(f"  {key}: ${value:,.2f}")

    print("\nOur engine (forward-looking recoverable ARR):")
    print(f"  finding_count: {engine['finding_count']}")
    print(f"  unique_subscriptions: {engine['unique_subscriptions']}")
    print(f"  raw_sum_arr: ${raw_arr:,.2f}")
    print(f"  primary_recoverable_arr: ${primary_arr:,.2f}")
    print(f"  secondary_excluded_arr: ${secondary_arr:,.2f}")
    print(f"  recoverable_arr_deduped: ${primary_arr:,.2f}")

    print("\nBy rule (count, ARR):")
    for rule_id, stats in sorted(engine["by_rule"].items(), key=lambda x: -x[1]["arr"]):
        print(f"  {rule_id}: {stats['count']} findings, ${stats['arr']:,.2f}")


if __name__ == "__main__":
    main()
