from collections.abc import Callable
from dataclasses import dataclass

from verification.context import AuditContext
from verification.types import RuleFinding


@dataclass
class RuleDefinition:
    rule_id: str
    name: str
    category: str
    requires_crm: bool = False
    requires_credit_data: bool = False
    requires_manual_override: bool = False
    evaluate: Callable[[AuditContext], list[RuleFinding]] | None = None


def _import_evaluate(module_path: str, func_name: str = "evaluate"):
    import importlib

    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)


RULES: list[RuleDefinition] = [
    RuleDefinition(
        "expired_discount_still_applied",
        "Expired Discount Still Applied",
        "discounts",
        evaluate=_import_evaluate("verification.rules.expired_discount"),
    ),
    RuleDefinition(
        "legacy_pricing_pre_catalog",
        "Legacy Pricing (Pre-Catalog Price)",
        "pricing",
        evaluate=_import_evaluate("verification.rules.legacy_pricing"),
    ),
    RuleDefinition(
        "renewal_price_drift",
        "Renewal Price Drift",
        "renewals",
        evaluate=_import_evaluate("verification.rules.renewal_drift"),
    ),
    RuleDefinition(
        "duplicate_discount_stacking",
        "Duplicate Discount Stacking",
        "discounts",
        evaluate=_import_evaluate("verification.rules.duplicate_discount"),
    ),
    RuleDefinition(
        "price_catalog_mismatch",
        "Price Catalog Mismatch",
        "pricing",
        evaluate=_import_evaluate("verification.rules.price_catalog_mismatch"),
    ),
    RuleDefinition(
        "grandfathered_without_contract",
        "Grandfathered Pricing Without Contract Exception",
        "pricing",
        evaluate=_import_evaluate("verification.rules.grandfathered_pricing"),
    ),
    RuleDefinition(
        "missing_scheduled_increase",
        "Missing Scheduled Price Increase",
        "pricing",
        evaluate=_import_evaluate("verification.rules.missing_scheduled_increase"),
    ),
    RuleDefinition(
        "invoice_subscription_price_mismatch",
        "Invoice vs Subscription Price Mismatch",
        "pricing",
        evaluate=_import_evaluate("verification.rules.invoice_pricing_mismatch"),
    ),
    RuleDefinition(
        "duplicate_active_subscriptions",
        "Duplicate Active Subscriptions",
        "subscriptions",
        evaluate=_import_evaluate("verification.rules.duplicate_subscriptions"),
    ),
    RuleDefinition(
        "billing_frequency_mismatch",
        "Billing Frequency Mismatch",
        "billing",
        evaluate=_import_evaluate("verification.rules.billing_frequency_mismatch"),
    ),
    RuleDefinition(
        "currency_inconsistency",
        "Currency Inconsistency Leakage",
        "billing",
        evaluate=_import_evaluate("verification.rules.currency_mismatch"),
    ),
    RuleDefinition(
        "credit_adjustment_leakage",
        "Credit / Adjustment Leakage",
        "credits",
        requires_credit_data=True,
        evaluate=_import_evaluate("verification.rules.credit_leakage"),
    ),
    RuleDefinition(
        "manual_override_pricing",
        "Manual Override Pricing",
        "overrides",
        requires_manual_override=True,
        evaluate=_import_evaluate("verification.rules.manual_overrides"),
    ),
    RuleDefinition(
        "discount_past_contract_end",
        "Discount Persistence Beyond Contract Terms",
        "discounts",
        evaluate=_import_evaluate("verification.rules.discount_persistence"),
    ),
    RuleDefinition(
        "seat_quantity_underbilling",
        "Seat / Quantity Underbilling",
        "usage",
        requires_crm=True,
        evaluate=_import_evaluate("verification.rules.seat_count_variance"),
    ),
    RuleDefinition(
        "contract_billing_price_divergence",
        "Contract vs Billing Price Divergence",
        "contracts",
        requires_crm=True,
        evaluate=_import_evaluate("verification.rules.contract_vs_billing"),
    ),
    RuleDefinition(
        "underpriced_renewal_vs_contract",
        "Underpriced Renewals vs Contract Terms",
        "renewals",
        requires_crm=True,
        evaluate=_import_evaluate("verification.rules.underpriced_renewals"),
    ),
    RuleDefinition(
        "free_plan_never_converted",
        "Free Plan Never Converted",
        "monetization",
        evaluate=_import_evaluate("verification.rules.free_plan_leakage"),
    ),
    RuleDefinition(
        "discount_abuse_frequency",
        "Discount Abuse Frequency Pattern",
        "discounts",
        evaluate=_import_evaluate("verification.rules.discount_abuse"),
    ),
    RuleDefinition(
        "legacy_sku_pricing_drift",
        "Legacy SKU Pricing Drift",
        "pricing",
        evaluate=_import_evaluate("verification.rules.legacy_sku_drift"),
    ),
]


def get_all_rules() -> list[RuleDefinition]:
    return RULES
