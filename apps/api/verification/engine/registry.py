from __future__ import annotations

from verification.rules.protocol import RuleModule
from verification.rules.pricing.contract_billing_divergence import rule as contract_billing_divergence
from verification.rules.pricing.legacy_pricing import rule as legacy_pricing
from verification.rules.pricing.price_catalog_mismatch import rule as price_catalog_mismatch
from verification.rules.pricing.grandfathered_pricing import rule as grandfathered_pricing
from verification.rules.pricing.missing_scheduled_increase import rule as missing_scheduled_increase
from verification.rules.pricing.renewal_price_drift import rule as renewal_price_drift
from verification.rules.pricing.manual_price_override import rule as manual_price_override
from verification.rules.pricing.incorrect_seat_price import rule as incorrect_seat_price
from verification.rules.pricing.incorrect_addon_price import rule as incorrect_addon_price
from verification.rules.discounts.expired_discount import rule as expired_discount
from verification.rules.discounts.discount_stacking import rule as discount_stacking
from verification.rules.discounts.duplicate_discount import rule as duplicate_discount
from verification.rules.discounts.permanent_promotional_discount import rule as permanent_promotional_discount
from verification.rules.discounts.excessive_discount import rule as excessive_discount
from verification.rules.discounts.discount_wrong_product import rule as discount_wrong_product
from verification.rules.billing.invoice_price_mismatch import rule as invoice_price_mismatch
from verification.rules.billing.duplicate_subscription import rule as duplicate_subscription
from verification.rules.billing.billing_frequency_mismatch import rule as billing_frequency_mismatch
from verification.rules.billing.active_subscription_not_billing import rule as active_subscription_not_billing
from verification.rules.billing.cancelled_subscription_still_billing import rule as cancelled_subscription_still_billing
from verification.rules.billing.missing_expected_invoice import rule as missing_expected_invoice
from verification.rules.credits.credit_leakage import rule as credit_leakage
from verification.rules.credits.duplicate_credit import rule as duplicate_credit
from verification.rules.data_quality.duplicate_customer import rule as duplicate_customer
from verification.rules.data_quality.currency_mismatch import rule as currency_mismatch
from verification.rules.data_quality.orphaned_records import rule as orphaned_records

ALL_RULE_MODULES: list[RuleModule] = [
    legacy_pricing,
    contract_billing_divergence,
    price_catalog_mismatch,
    grandfathered_pricing,
    missing_scheduled_increase,
    renewal_price_drift,
    manual_price_override,
    incorrect_seat_price,
    incorrect_addon_price,
    expired_discount,
    discount_stacking,
    duplicate_discount,
    permanent_promotional_discount,
    excessive_discount,
    discount_wrong_product,
    invoice_price_mismatch,
    duplicate_subscription,
    billing_frequency_mismatch,
    active_subscription_not_billing,
    cancelled_subscription_still_billing,
    missing_expected_invoice,
    credit_leakage,
    duplicate_credit,
    duplicate_customer,
    currency_mismatch,
    orphaned_records,
]


def get_all_rules() -> list[RuleModule]:
    return list(ALL_RULE_MODULES)


def get_rule_module(rule_id: str) -> RuleModule | None:
    for module in ALL_RULE_MODULES:
        if module.spec.rule_id == rule_id:
            return module
    return None
