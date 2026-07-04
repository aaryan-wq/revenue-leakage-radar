"""Export canonical company data to fuzzed platform CSV files."""

from __future__ import annotations

import csv
import random
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from core.enums import FileType

CANONICAL_FILE_MAP: dict[str, FileType] = {
    "customers": FileType.CUSTOMERS,
    "subscriptions": FileType.SUBSCRIPTIONS,
    "invoices": FileType.INVOICES,
    "invoice_line_items": FileType.INVOICE_LINE_ITEMS,
    "coupons": FileType.COUPONS,
    "price_catalog": FileType.PRICE_CATALOG,
    "crm_accounts": FileType.CRM_ACCOUNTS,
    "crm_contracts": FileType.CRM_CONTRACTS,
}

HEADER_ALIASES: dict[str, list[str]] = {
    "customer_id": ["customer_id", "Customer ID", "customerId", "Customer_Id", "cust_id", "CustId"],
    "subscription_id": ["subscription_id", "Subscription ID", "subscriptionId", "Sub ID", "sub_id"],
    "invoice_id": ["invoice_id", "Invoice ID", "invoiceId", "Invoice_Id"],
    "line_item_id": ["line_item_id", "Line Item ID", "lineItemId", "LineItemId"],
    "product_id": ["product_id", "Product ID", "productId", "Product_Id"],
    "invoice_number": ["invoice_number", "Invoice Number", "invoiceNumber", "InvoiceNumber"],
    "unit_price": ["unit_price", "Unit Price", "unitPrice", "UnitPrice"],
    "list_price": ["list_price", "List Price", "listPrice", "ListPrice"],
    "billing_interval": ["billing_interval", "Billing Interval", "billingInterval", "interval"],
    "start_date": ["start_date", "Start Date", "startDate", "StartDate"],
    "renewal_date": ["renewal_date", "Renewal Date", "renewalDate"],
    "invoice_date": ["invoice_date", "Invoice Date", "invoiceDate", "InvoiceDate"],
    "effective_date": ["effective_date", "Effective Date", "effectiveDate"],
    "period_start": ["period_start", "Period Start", "periodStart"],
    "period_end": ["period_end", "Period End", "periodEnd"],
    "coupon_id": ["coupon_id", "Coupon ID", "couponId"],
    "credit_amount": ["credit_amount", "Credit Amount", "creditAmount"],
    "is_manual_override": ["is_manual_override", "Manual Override", "isManualOverride"],
    "seat_count": ["seat_count", "Seat Count", "seatCount", "Seats"],
    "account_id": ["account_id", "Account ID", "accountId"],
    "contract_id": ["contract_id", "Contract ID", "contractId"],
}

PLATFORM_EXTRA_COLUMNS: dict[str, list[str]] = {
    "stripe": ["stripe_customer_id", "amount_due", "subscription_item"],
    "chargebee": ["plan_id", "cf_region"],
    "maxio": ["component_id", "allocation"],
    "zuora": ["SubscriptionNumber", "AccountNumber"],
    "paddle": ["paddle_subscription_id", "passthrough"],
    "recurly": ["recurly_uuid", "plan_code"],
    "hubspot": ["hs_object_id", "hubspot_owner_id"],
    "salesforce": ["SFDC_Id", "Account_Owner"],
    "pipedrive": ["pd_id", "org_name"],
    "attio": ["attio_record_id", "workspace_id"],
}

DATE_FORMATS = ["%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d"]


@dataclass
class CsvFuzzConfig:
    platform: str = "generic"
    header_style: str = "random"
    delimiter: str = ","
    line_ending: str = "\n"
    shuffle_columns: bool = True
    add_blank_rows: bool = False
    add_extra_columns: bool = True
    drop_optional_columns: bool = False
    whitespace_pad: bool = False
    date_format: str | None = None
    omit_files: set[str] | None = None


def _style_header(canonical: str, style: str, rng: random.Random) -> str:
    aliases = HEADER_ALIASES.get(canonical, [canonical])
    if style == "random":
        return rng.choice(aliases)
    if style == "snake":
        return canonical
    if style == "camel":
        parts = canonical.split("_")
        return parts[0] + "".join(p.capitalize() for p in parts[1:])
    if style == "pascal":
        return "".join(p.capitalize() for p in canonical.split("_"))
    if style == "title":
        return canonical.replace("_", " ").title()
    return rng.choice(aliases)


def _public_row(row: dict[str, Any]) -> dict[str, str]:
    return {k: str(v) for k, v in row.items() if not k.startswith("_")}


def _fuzz_date(value: str, fmt: str | None, rng: random.Random) -> str:
    if not value or not re.match(r"^\d{4}-\d{2}-\d{2}", value):
        return value
    if fmt is None:
        fmt = rng.choice(DATE_FORMATS)
    from datetime import date

    d = date.fromisoformat(value[:10])
    return d.strftime(fmt)


def export_csvs(
    state_rows: dict[str, list[dict[str, Any]]],
    output_dir: Path,
    rng: random.Random,
    config: CsvFuzzConfig | None = None,
) -> dict[str, Path]:
    config = config or CsvFuzzConfig()
    output_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}
    omit = config.omit_files or set()

    for file_key, rows in state_rows.items():
        if file_key in omit or not rows:
            continue
        public = [_public_row(r) for r in rows]
        if not public:
            continue

        canonical_fields = list(public[0].keys())
        if config.shuffle_columns:
            rng.shuffle(canonical_fields)

        optional = {"crm_id", "sku", "extended_price", "period_start", "period_end", "credit_amount"}
        if config.drop_optional_columns:
            canonical_fields = [f for f in canonical_fields if f not in optional or rng.random() > 0.5]

        header_map = {
            field: _style_header(field, config.header_style, rng) for field in canonical_fields
        }
        headers = [header_map[f] for f in canonical_fields]

        if config.add_extra_columns and config.platform in PLATFORM_EXTRA_COLUMNS:
            for extra in rng.sample(
                PLATFORM_EXTRA_COLUMNS[config.platform],
                k=min(2, len(PLATFORM_EXTRA_COLUMNS[config.platform])),
            ):
                headers.append(extra)

        path = output_dir / f"{file_key}.csv"
        line_ending = config.line_ending
        with path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle, delimiter=config.delimiter, lineterminator=line_ending)
            writer.writerow(headers)
            if config.add_blank_rows and rng.random() < 0.3:
                writer.writerow([""] * len(headers))
            for row in public:
                values = []
                for field in canonical_fields:
                    val = row.get(field, "")
                    if field.endswith("_date") or field in ("expires_at",):
                        val = _fuzz_date(val, config.date_format, rng)
                    if config.whitespace_pad and val:
                        val = f"  {val}  "
                    values.append(val)
                if config.add_extra_columns and config.platform in PLATFORM_EXTRA_COLUMNS:
                    for _ in range(len(headers) - len(canonical_fields)):
                        values.append("")
                writer.writerow(values)
        written[file_key] = path

    return written
