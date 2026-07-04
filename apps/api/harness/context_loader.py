"""Load canonical CSV rows into an AuditContext for rule evaluation."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from harness.money import parse_date, to_decimal
from models import Coupon, CrmAccount, CrmContract, Customer, Invoice, InvoiceLineItem, PriceCatalog, Subscription
from verification.context import AuditContext


@dataclass
class IdMaps:
    customer: dict[str, uuid.UUID]
    subscription: dict[str, uuid.UUID]
    invoice: dict[str, uuid.UUID]
    account: dict[str, uuid.UUID]


def _load_rows_from_dir(data_dir: Path, filename: str, *, fallbacks: tuple[str, ...] = ()) -> list[dict[str, str]]:
    for candidate in (filename, *fallbacks):
        path = data_dir / candidate
        if path.exists():
            import csv

            with path.open(encoding="utf-8-sig", newline="") as handle:
                return list(csv.DictReader(handle))
    return []


CSV_ENTITY_FILES = (
    "customers.csv",
    "subscriptions.csv",
    "invoices.csv",
    "invoice_line_items.csv",
    "coupons.csv",
    "price_catalog.csv",
    "crm_accounts.csv",
    "crm_contracts.csv",
)


def load_context_from_csv_dir(data_dir: Path) -> tuple[AuditContext, IdMaps]:
    """Load frozen regression CSVs into a canonical context."""
    rows: dict[str, list[dict[str, Any]]] = {
        "customers": _load_rows_from_dir(data_dir, "customers.csv"),
        "subscriptions": _load_rows_from_dir(data_dir, "subscriptions.csv"),
        "invoices": _load_rows_from_dir(data_dir, "invoices.csv"),
        "invoice_line_items": _load_rows_from_dir(data_dir, "invoice_line_items.csv"),
        "coupons": _load_rows_from_dir(data_dir, "coupons.csv"),
        "price_catalog": _load_rows_from_dir(data_dir, "price_catalog.csv"),
        "crm_accounts": _load_rows_from_dir(data_dir, "crm_accounts.csv", fallbacks=("accounts.csv",)),
        "crm_contracts": _load_rows_from_dir(data_dir, "crm_contracts.csv", fallbacks=("contracts.csv",)),
    }
    return build_context_from_state(rows)


def build_context_from_state(
    state_rows: dict[str, list[dict[str, Any]]],
    company_id: uuid.UUID | None = None,
    audit_id: uuid.UUID | None = None,
) -> tuple[AuditContext, IdMaps]:
    company_id = company_id or uuid.uuid4()
    audit_id = audit_id or uuid.uuid4()
    id_maps = IdMaps(customer={}, subscription={}, invoice={}, account={})

    customers: list[Customer] = []
    for row in state_rows.get("customers", []):
        cust_uuid = uuid.uuid4()
        id_maps.customer[row["customer_id"]] = cust_uuid
        customers.append(
            Customer(
                id=cust_uuid,
                company_id=company_id,
                external_customer_id=row["customer_id"],
                crm_id=row.get("crm_id") or None,
                name=row.get("name"),
            )
        )

    subscriptions: list[Subscription] = []
    for row in state_rows.get("subscriptions", []):
        sub_uuid = uuid.uuid4()
        id_maps.subscription[row["subscription_id"]] = sub_uuid
        cust_key = row["customer_id"]
        subscriptions.append(
            Subscription(
                id=sub_uuid,
                customer_id=id_maps.customer[cust_key],
                external_subscription_id=row["subscription_id"],
                product_id=row.get("product_id"),
                plan=row.get("plan"),
                quantity=int(row["quantity"]) if row.get("quantity") else None,
                billing_interval=row.get("billing_interval"),
                price=to_decimal(row.get("price")),
                currency=row.get("currency"),
                start_date=parse_date(row.get("start_date")),
                renewal_date=parse_date(row.get("renewal_date")),
                status=row.get("status"),
                coupon_id=row.get("coupon_id") or None,
            )
        )

    invoices: list[Invoice] = []
    for row in state_rows.get("invoices", []):
        inv_uuid = uuid.uuid4()
        id_maps.invoice[row["invoice_id"]] = inv_uuid
        sub_key = row.get("subscription_id") or ""
        invoices.append(
            Invoice(
                id=inv_uuid,
                customer_id=id_maps.customer[row["customer_id"]],
                subscription_id=id_maps.subscription.get(sub_key),
                external_invoice_id=row["invoice_id"],
                invoice_number=row["invoice_number"],
                invoice_date=parse_date(row.get("invoice_date")),
                period_start=parse_date(row.get("period_start")),
                period_end=parse_date(row.get("period_end")),
                subtotal=to_decimal(row.get("subtotal")),
                discount=to_decimal(row.get("discount")),
                total=to_decimal(row.get("total")),
                credit_amount=to_decimal(row.get("credit_amount")),
                currency=row.get("currency"),
            )
        )

    line_items: list[InvoiceLineItem] = []
    for row in state_rows.get("invoice_line_items", []):
        inv_key = row["invoice_id"]
        resolved_invoice_id = id_maps.invoice.get(inv_key) if inv_key else None
        referenced_invoice_id = inv_key if inv_key and resolved_invoice_id is None else None
        sub_key = row.get("subscription_id") or ""
        cust_key = row.get("customer_id") or ""
        line_items.append(
            InvoiceLineItem(
                id=uuid.uuid4(),
                invoice_id=resolved_invoice_id,
                referenced_invoice_id=referenced_invoice_id,
                customer_id=id_maps.customer.get(cust_key),
                subscription_id=id_maps.subscription.get(sub_key),
                external_line_item_id=row.get("line_item_id"),
                product_id=row.get("product_id"),
                sku=row.get("sku"),
                quantity=int(row["quantity"]) if row.get("quantity") else None,
                unit_price=to_decimal(row.get("unit_price")),
                extended_price=to_decimal(row.get("extended_price")),
                billing_interval=row.get("billing_interval"),
                line_item_date=parse_date(row.get("line_item_date")),
                currency=row.get("currency"),
                is_manual_override=str(row.get("is_manual_override", "")).lower() == "true",
            )
        )

    coupons: list[Coupon] = []
    for row in state_rows.get("coupons", []):
        coupons.append(
            Coupon(
                id=uuid.uuid4(),
                company_id=company_id,
                code=row["code"],
                discount_type=row.get("discount_type"),
                discount_value=to_decimal(row.get("discount_value")),
                expires_at=parse_date(row.get("expires_at")),
                active=str(row.get("active", "true")).lower() == "true",
            )
        )

    price_catalog: list[PriceCatalog] = []
    for row in state_rows.get("price_catalog", []):
        price_catalog.append(
            PriceCatalog(
                id=uuid.uuid4(),
                company_id=company_id,
                product_id=row["product_id"],
                sku=row.get("sku"),
                version=row.get("version"),
                effective_date=parse_date(row.get("effective_date")),
                list_price=to_decimal(row.get("list_price")),
                currency=row.get("currency"),
                billing_interval=row.get("billing_interval"),
            )
        )

    crm_accounts: list[CrmAccount] = []
    for row in state_rows.get("crm_accounts", []):
        acct_uuid = uuid.uuid4()
        id_maps.account[row["account_id"]] = acct_uuid
        cust_key = row.get("customer_id") or ""
        crm_accounts.append(
            CrmAccount(
                id=acct_uuid,
                company_id=company_id,
                external_account_id=row["account_id"],
                customer_id=id_maps.customer.get(cust_key),
                name=row.get("name"),
                seat_count=int(row["seat_count"]) if row.get("seat_count") else None,
            )
        )

    crm_contracts: list[CrmContract] = []
    for row in state_rows.get("crm_contracts", []):
        acct_key = row.get("account_id") or ""
        cust_key = row.get("customer_id") or ""
        crm_contracts.append(
            CrmContract(
                id=uuid.uuid4(),
                company_id=company_id,
                external_contract_id=row["contract_id"],
                account_id=id_maps.account.get(acct_key),
                customer_id=id_maps.customer.get(cust_key),
                contract_price=to_decimal(row.get("contract_price")),
                price_increase_date=parse_date(row.get("price_increase_date") or None),
                expected_renewal_price=to_decimal(row.get("expected_renewal_price")),
                start_date=parse_date(row.get("start_date")),
                end_date=parse_date(row.get("end_date")),
                seat_count=int(row["seat_count"]) if row.get("seat_count") else None,
            )
        )

    has_credit = any(i.credit_amount is not None and i.credit_amount > 0 for i in invoices)
    has_manual = any(li.is_manual_override for li in line_items)

    ctx = AuditContext(
        audit_id=audit_id,
        company_id=company_id,
        customers=customers,
        subscriptions=subscriptions,
        invoices=invoices,
        line_items=line_items,
        coupons=coupons,
        price_catalog=price_catalog,
        crm_accounts=crm_accounts,
        crm_contracts=crm_contracts,
        has_crm=bool(crm_accounts or crm_contracts),
        has_credit_data=has_credit,
        has_manual_override_data=has_manual,
    )
    return ctx, id_maps


def state_to_rows(state) -> dict[str, list[dict[str, Any]]]:
    return {
        "customers": state.customers,
        "subscriptions": state.subscriptions,
        "invoices": state.invoices,
        "invoice_line_items": state.line_items,
        "coupons": state.coupons,
        "price_catalog": state.price_catalog,
        "crm_accounts": state.crm_accounts,
        "crm_contracts": state.crm_contracts,
    }
