"""Fictitious companies with bottom-up justified annual leakage for model calibration."""

from tests.estimator.test_engine import PROFILE_A, PROFILE_B

# Justified leakage = independent audit-style estimate from explicit billing mechanics.
# Overlap between mechanisms is already baked into the justified total.

PILOT_STARTER = {
    **PROFILE_A,
    "profile.arr_amount": 2_000_000,
    "profile.customer_count": 80,
}

ACME_CLEAN = {
    **PROFILE_A,
    "profile.arr_amount": 5_000_000,
    "profile.customer_count": 200,
}

MERIDIAN_MODERATE = {
    **PROFILE_A,
    "profile.arr_amount": 18_000_000,
    "profile.customer_count": 1200,
    "pricing.models": ["flat", "per_seat"],
    "product.billable_count": "3_5",
    "product.addons": True,
    "contracts.negotiated_arr_pct": "26_50",
    "contracts.custom_pricing": "yes",
    "contracts.grandfathering": "sometimes",
    "contracts.renewal_increases": "manual",
    "discounts.frequency": "occasional",
    "discounts.expiry_handling": "manual_finance",
    "discounts.expiry_confidence": 3,
    "changes.pricing_changes_24mo": "2_3",
    "operations.manual_override_frequency": "sometimes",
    "operations.manual_change_logging": "partial",
    "seats.reconciliation": "manual",
    "quote_to_bill.quote_automation": "partial",
    "controls.monthly_reconciliation": "quarterly",
    "controls.billing_qa": "sometimes",
    "controls.invoice_price_qa": "sometimes",
    "discounts.stacking_policy": "limited",
    "operations.credit_memo_process": "manual",
    "operations.churn_billing_cutoff": "within_week",
    "operations.invoice_cadence": "scheduled",
    "operations.customer_dedup": "manual",
    "confidence.billing_confidence": 3,
    "quote_to_bill.finance_sales_disagreement": "sometimes",
    "operations.unticketed_adjustments": "sometimes",
    "controls.revenue_recognition_review": "quarterly",
}

VERTEX_MESSY = {
    **PROFILE_B,
    "profile.arr_amount": 25_000_000,
    "profile.customer_count": 120,
}

NOVA_ENTERPRISE = {
    **PROFILE_B,
    "profile.arr_amount": 40_000_000,
    "profile.customer_count": 85,
}

CALIBRATION_CASES = [
    {
        "id": "pilot_starter",
        "name": "Pilot Starter",
        "answers": PILOT_STARTER,
        "justified_leakage_usd": 9_000,
        "justified_pct_arr": 0.45,
        "rationale": (
            "Single product, Stripe, no discounts. ~40 accounts with minor renewal drift "
            "and billing execution residuals at ~$225/yr each (~$9k)."
        ),
    },
    {
        "id": "acme_clean",
        "name": "Acme Clean",
        "answers": ACME_CLEAN,
        "justified_leakage_usd": 25_000,
        "justified_pct_arr": 0.5,
        "rationale": (
            "Mature billing ops. Residual catalog/version drift on ~5% of ARR at ~1% leakage (~$25k)."
        ),
    },
    {
        "id": "meridian_moderate",
        "name": "Meridian Moderate",
        "answers": MERIDIAN_MODERATE,
        "justified_leakage_usd": 180_000,
        "justified_pct_arr": 1.0,
        "rationale": (
            "$18M ARR, 1,200 customers. Occasional grandfathering (~$55k), manual discount expiry "
            "on ~$5.4M discount pool (~$48k), manual seat reconciliation (~$32k), contract drift on "
            "~38% negotiated ARR (~$45k). Overlap-adjusted total ~$180k (1.0% ARR). "
            "Industry context for moderate B2B SaaS at this scale often spans 0.8% to 2.5% ARR."
        ),
    },
    {
        "id": "vertex_messy",
        "name": "Vertex Messy",
        "answers": VERTEX_MESSY,
        "justified_leakage_usd": 750_000,
        "justified_pct_arr": 3.0,
        "rationale": (
            "$25M ARR, very high complexity. Heavy grandfathering (~$220k), expired/manual discounts "
            "on ~$17.5M discount exposure (~$180k), quote-to-bill gaps on enterprise contracts (~$200k), "
            "migration errors (~$90k), manual overrides (~$120k). Overlap-adjusted ~$750k (3.0% ARR)."
        ),
    },
    {
        "id": "nova_enterprise",
        "name": "Nova Enterprise",
        "answers": NOVA_ENTERPRISE,
        "justified_leakage_usd": 1_200_000,
        "justified_pct_arr": 3.0,
        "rationale": (
            "$40M ARR, same risk profile as Vertex scaled up. Enterprise contract + discount + migration "
            "mechanisms compound to ~$1.2M (3.0% ARR) after overlap."
        ),
    },
]
