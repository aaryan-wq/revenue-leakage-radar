#!/usr/bin/env python3
"""Validate AcmeCRM fixture triggers expected verification rules."""

from __future__ import annotations

import csv
import json
import sys
import uuid
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "apps" / "api"))

from models import Coupon, Invoice, InvoiceLineItem, PriceCatalog, Subscription
from verification.context import AuditContext
from verification.rules.duplicate_discount import evaluate as eval_duplicate_discount
from verification.rules.expired_discount import evaluate as eval_expired_discount
from verification.rules.grandfathered_pricing import evaluate as eval_grandfathered
from verification.rules.invoice_pricing_mismatch import evaluate as eval_invoice_mismatch
from verification.rules.legacy_sku_drift import evaluate as eval_legacy_sku

DATA_DIR = ROOT / "testdata" / "acmecrm"


def parse_date(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value).replace(tzinfo=timezone.utc)


def parse_decimal(value: str | None) -> Decimal | None:
    if value is None or value == "":
        return None
    return Decimal(str(value))


def load_csv(name: str) -> list[dict[str, str]]:
    with (DATA_DIR / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def build_context() -> AuditContext:
    company_id = uuid.uuid4()
    audit_id = uuid.uuid4()

    id_map: dict[str, uuid.UUID] = {
        "customer": {},
        "subscription": {},
        "invoice": {},
    }

    customers_rows = load_csv("customers.csv")
    for row in customers_rows:
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

    sub_ext_by_uuid = {sub.id: sub.external_subscription_id for sub in subscriptions}

    return AuditContext(
        audit_id=audit_id,
        company_id=company_id,
        subscriptions=subscriptions,
        invoices=invoices,
        line_items=line_items,
        coupons=coupons,
        price_catalog=price_catalog,
        has_crm=False,
    ), sub_ext_by_uuid


def unique_subs(findings, sub_ext_by_uuid) -> set[str]:
    result: set[str] = set()
    for finding in findings:
        if finding.subscription_id:
            ext = sub_ext_by_uuid.get(uuid.UUID(str(finding.subscription_id)))
            if ext:
                result.add(ext)
    return result


def main() -> None:
    manifest = json.loads((DATA_DIR / "manifest.json").read_text(encoding="utf-8"))
    ctx, sub_ext = build_context()

    checks = [
        ("expired_discount_still_applied", eval_expired_discount, "expired_discount_still_applied"),
        ("legacy_sku_pricing_drift", eval_legacy_sku, "legacy_pricing_after_renewal"),
        ("invoice_subscription_price_mismatch", eval_invoice_mismatch, "invoice_line_item_price_mismatch"),
        ("duplicate_discount_stacking", eval_duplicate_discount, "duplicate_discount_stacking"),
        ("grandfathered_without_contract", eval_grandfathered, "undercharged_subscriptions"),
    ]

    print("AcmeCRM dataset rule verification")
    print("-" * 60)
    all_ok = True

    for rule_id, evaluator, manifest_key in checks:
        findings = evaluator(ctx)
        detected = unique_subs(findings, sub_ext)
        expected_ids = set(manifest["injected_scenarios"][manifest_key]["subscription_ids"])

        ok = expected_ids.issubset(detected)
        all_ok = all_ok and ok
        status = "OK" if ok else "FAIL"
        print(f"[{status}] {rule_id}")
        print(f"       findings: {len(findings)} | subscriptions detected: {len(detected)} | expected subs: {len(expected_ids)}")
        if not ok:
            missing = sorted(expected_ids - detected)
            print(f"       missing: {missing[:5]}{'...' if len(missing) > 5 else ''}")

    print("-" * 60)
    if not all_ok:
        sys.exit(1)
    print("All injected scenarios detected by the rule engine.")


if __name__ == "__main__":
    main()
