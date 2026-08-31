from typing import Any

from estimator.questionnaire.schema import load_priors


def normalize_answers(answers: dict[str, Any]) -> dict[str, Any]:
    priors = load_priors()
    fx = priors.get("fx_to_usd", {"USD": 1.0})
    normalized = dict(answers)
    arr = answers.get("profile.arr_amount")
    currency = answers.get("profile.arr_currency") or "USD"
    if arr is not None:
        rate = float(fx.get(currency, 1.0))
        normalized["arr_usd"] = float(arr) * rate
        normalized["profile.arr_currency"] = currency
    else:
        normalized["arr_usd"] = 0.0

    confidence = answers.get("profile.arr_confidence", "approximate")
    uncertainty = {"exact": 0.02, "approximate": 0.05, "rough": 0.15}.get(confidence, 0.05)
    billing_conf = answers.get("confidence.billing_confidence")
    if billing_conf is not None:
        try:
            score = float(billing_conf)
            if score <= 2:
                uncertainty = max(uncertainty, 0.10)
            elif score <= 3:
                uncertainty = max(uncertainty, 0.06)
        except (TypeError, ValueError):
            pass
    normalized["arr_uncertainty"] = uncertainty

    models = answers.get("pricing.models") or []
    if isinstance(models, list):
        normalized["pricing.usage_based"] = "usage" in models
        normalized["pricing.seat_based"] = "per_seat" in models
    return normalized


def derive_segments(normalized: dict[str, Any]) -> dict[str, float]:
    arr = normalized.get("arr_usd", 0.0)
    discount_freq = normalized.get("discounts.frequency", "never")
    discount_share = {
        "never": 0.05,
        "rare": 0.15,
        "occasional": 0.38,
        "common": 0.52,
        "nearly_all": 0.70,
    }.get(discount_freq, 0.20)

    negotiated_pct = _pct_map(normalized.get("contracts.negotiated_arr_pct"))

    usage = normalized.get("pricing.usage_based") is True
    usage_share = 0.35 if usage else 0.05
    seat = normalized.get("pricing.seat_based") is True
    seat_share = 0.40 if seat else 0.10
    addon = normalized.get("product.addons") is True
    addon_share = 0.15 if addon else 0.05
    multi_currency = normalized.get("international.multi_currency") is True
    intl_share = 0.25 if multi_currency else 0.05

    credit_process = normalized.get("operations.credit_memo_process", "unknown")
    credit_share = {
        "automated": 0.02,
        "reviewed": 0.04,
        "manual": 0.08,
        "ad_hoc": 0.12,
        "unknown": 0.06,
    }.get(credit_process, 0.06)

    churn_cutoff = normalized.get("operations.churn_billing_cutoff", "unknown")
    billing_exec_share = {
        "immediate": 0.08,
        "same_day": 0.10,
        "within_week": 0.14,
        "manual": 0.22,
        "unknown": 0.16,
    }.get(churn_cutoff, 0.16)

    invoice_cadence = normalized.get("operations.invoice_cadence", "unknown")
    invoice_qa = normalized.get("controls.invoice_price_qa", "unknown")
    invoice_weight = _invoice_weight(invoice_cadence, invoice_qa)

    return {
        "arr": arr,
        "contract_arr": arr * negotiated_pct,
        "discount_arr": arr * discount_share,
        "usage_arr": arr * usage_share,
        "seat_arr": arr * seat_share,
        "addon_arr": arr * addon_share,
        "international_arr": arr * intl_share,
        "credit_arr": arr * credit_share,
        "billing_execution_arr": arr * billing_exec_share,
        "invoice_arr": arr * invoice_weight,
        "negotiated_pct": negotiated_pct,
        "discount_share": discount_share,
    }


def _invoice_weight(cadence: str, qa: str) -> float:
    cadence_weight = {
        "automated": 0.85,
        "scheduled": 0.90,
        "manual": 1.0,
        "ad_hoc": 1.05,
        "unknown": 0.95,
    }.get(cadence, 0.95)
    qa_weight = {
        "always": 0.85,
        "usually": 0.90,
        "sometimes": 0.95,
        "rarely": 1.0,
        "never": 1.05,
        "unknown": 0.98,
    }.get(qa, 0.98)
    return min(cadence_weight * qa_weight, 1.1)


def _pct_map(value: str | None) -> float:
    mapping = {
        "0": 0.0,
        "1_25": 0.13,
        "26_50": 0.38,
        "51_75": 0.63,
        "76_100": 0.88,
    }
    return mapping.get(value or "0", 0.0)
