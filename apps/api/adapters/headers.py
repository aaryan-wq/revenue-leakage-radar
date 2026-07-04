"""Shared header normalization utilities for platform adapters."""

import re

from canonical.fields import CANONICAL_FIELDS
from core.enums import FileType, Platform

HEADER_SYNONYMS: dict[str, str] = {
    "subscription id": "subscription_id",
    "subscription_id": "subscription_id",
    "sub id": "subscription_id",
    "customer id": "customer_id",
    "customer_id": "customer_id",
    "cust id": "customer_id",
    "invoice id": "invoice_id",
    "invoice_id": "invoice_id",
    "line item id": "line_item_id",
    "line_item_id": "line_item_id",
    "coupon id": "coupon_id",
    "coupon_id": "coupon_id",
    "product id": "product_id",
    "product_id": "product_id",
    "invoice number": "invoice_number",
    "invoice_number": "invoice_number",
    "unit price": "unit_price",
    "unit_price": "unit_price",
    "extended price": "extended_price",
    "extended_price": "extended_price",
    "list price": "list_price",
    "list_price": "list_price",
    "discount type": "discount_type",
    "discount_type": "discount_type",
    "discount value": "discount_value",
    "discount_value": "discount_value",
    "billing interval": "billing_interval",
    "billing_interval": "billing_interval",
    "start date": "start_date",
    "start_date": "start_date",
    "renewal date": "renewal_date",
    "renewal_date": "renewal_date",
    "effective date": "effective_date",
    "effective_date": "effective_date",
    "invoice date": "invoice_date",
    "invoice_date": "invoice_date",
    "line item date": "line_item_date",
    "line_item_date": "line_item_date",
    "customer name": "name",
    "customer_name": "name",
    "crm id": "crm_id",
    "crm_id": "crm_id",
    "period start": "period_start",
    "period_start": "period_start",
    "period end": "period_end",
    "period_end": "period_end",
    "expires at": "expires_at",
    "expires_at": "expires_at",
}


def normalize_header(header: str) -> str:
    cleaned = header.strip().lower()
    cleaned = re.sub(r"[^a-z0-9]+", " ", cleaned).strip()
    return cleaned


def map_header_to_canonical(header: str, file_type: FileType) -> str | None:
    normalized = normalize_header(header)
    if normalized in HEADER_SYNONYMS:
        canonical = HEADER_SYNONYMS[normalized]
        if canonical in CANONICAL_FIELDS.get(file_type, []):
            return canonical

    snake = normalized.replace(" ", "_")
    if snake in CANONICAL_FIELDS.get(file_type, []):
        return snake

    return None


def build_column_mappings(file_headers: dict[FileType, list[str]]) -> dict[str, dict[str, str]]:
    mappings: dict[str, dict[str, str]] = {}
    for file_type, headers in file_headers.items():
        file_map: dict[str, str] = {}
        for header in headers:
            canonical = map_header_to_canonical(header, file_type)
            if canonical:
                file_map[header] = canonical
        if file_map:
            mappings[file_type.value] = file_map
    return mappings
