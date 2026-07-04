"""Stripe CSV adapter, platform detection and header hints."""

from adapters.generic.adapter import GenericAdapter
from adapters.headers import build_column_mappings
from core.enums import FileType, Platform

STRIPE_HEADER_HINTS: list[str] = [
    "stripe_customer_id",
    "subscription_item",
    "amount_due",
]


class StripeAdapter(GenericAdapter):
    def detect_platform(self, file_headers: dict[FileType, list[str]]) -> Platform:
        all_headers: set[str] = set()
        for headers in file_headers.values():
            all_headers.update(h.lower() for h in headers)
        if any(hint in all_headers for hint in STRIPE_HEADER_HINTS):
            return Platform.STRIPE
        return Platform.GENERIC

    def map_columns(self, file_headers: dict[FileType, list[str]]) -> dict[str, dict[str, str]]:
        return build_column_mappings(file_headers)
