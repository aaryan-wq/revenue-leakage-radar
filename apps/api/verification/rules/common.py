from __future__ import annotations

from verification.context import CanonicalContext, is_active_subscription

__all__ = ["CanonicalContext", "is_active_subscription", "should_skip_discounted_subscription"]


def should_skip_discounted_subscription(sub, invoice) -> bool:
    if sub is None:
        return False
    if not is_active_subscription(sub.status):
        return True
    if sub.coupon_id:
        return True
    if invoice and invoice.discount and invoice.discount > 0:
        return True
    return False
