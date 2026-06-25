import re

from canonical.fields import CANONICAL_FIELDS
from core.enums import FileType

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
    "period start": "period_start",
    "period_start": "period_start",
    "period end": "period_end",
    "period_end": "period_end",
    "expires at": "expires_at",
    "expires_at": "expires_at",
}

PLATFORM_HEADER_HINTS: dict[str, list[str]] = {
    "stripe": ["stripe_customer_id", "subscription_item", "amount_due"],
    "chargebee": ["subscription_id", "customer_id", "plan_id"],
    "maxio": ["subscription_id", "customer_id"],
    "zuora": ["subscriptionnumber", "accountnumber"],
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


def detect_platform_fallback(file_samples: dict[FileType, list[str]]) -> str:
    all_headers: set[str] = set()
    for headers in file_samples.values():
        all_headers.update(h.lower() for h in headers)

    for platform, hints in PLATFORM_HEADER_HINTS.items():
        if any(hint in all_headers for hint in hints):
            return platform

    return "generic"


def build_fallback_mappings(
    file_headers: dict[FileType, list[str]],
) -> tuple[str, dict[str, dict[str, str]]]:
    platform = detect_platform_fallback(file_headers)
    mappings: dict[str, dict[str, str]] = {}

    for file_type, headers in file_headers.items():
        file_map: dict[str, str] = {}
        for header in headers:
            canonical = map_header_to_canonical(header, file_type)
            if canonical:
                file_map[header] = canonical
        if file_map:
            mappings[file_type.value] = file_map

    return platform, mappings
