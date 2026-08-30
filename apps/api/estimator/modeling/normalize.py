from typing import Any

from estimator.questionnaire.schema import load_priors


def normalize_answers(answers: dict[str, Any]) -> dict[str, Any]:
    priors = load_priors()
    fx = priors.get("fx_to_usd", {"USD": 1.0})
    normalized = dict(answers)
    arr = answers.get("profile.arr_amount")
    currency = answers.get("profile.arr_currency") or "USD"
    # Currency may be stored on arr_amount answer value_text
    if arr is not None:
        rate = float(fx.get(currency, 1.0))
        normalized["arr_usd"] = float(arr) * rate
        normalized["profile.arr_currency"] = currency
    else:
        normalized["arr_usd"] = 0.0

    confidence = answers.get("profile.arr_confidence", "approximate")
    uncertainty = {"exact": 0.02, "approximate": 0.05, "rough": 0.15}.get(confidence, 0.05)
    normalized["arr_uncertainty"] = uncertainty
    return normalized


def derive_segments(normalized: dict[str, Any]) -> dict[str, float]:
    arr = normalized.get("arr_usd", 0.0)
    negotiated_pct = _pct_map(normalized.get("contracts.negotiated_arr_pct"))
    discount_freq = normalized.get("discounts.frequency", "never")
    discount_share = {
        "never": 0.05,
        "rare": 0.15,
        "occasional": 0.30,
        "common": 0.50,
        "nearly_all": 0.70,
    }.get(discount_freq, 0.20)

    usage = normalized.get("pricing.usage_based") is True
    usage_share = 0.35 if usage else 0.05
    seat = normalized.get("pricing.seat_based") is True
    seat_share = 0.40 if seat else 0.10
    addon = normalized.get("product.addons") is True
    addon_share = 0.15 if addon else 0.05
    multi_currency = normalized.get("international.multi_currency") is True
    intl_share = 0.25 if multi_currency else 0.05

    return {
        "arr": arr,
        "contract_arr": arr * negotiated_pct,
        "discount_arr": arr * discount_share,
        "usage_arr": arr * usage_share,
        "seat_arr": arr * seat_share,
        "addon_arr": arr * addon_share,
        "international_arr": arr * intl_share,
        "negotiated_pct": negotiated_pct,
        "discount_share": discount_share,
    }


def _pct_map(value: str | None) -> float:
    mapping = {
        "0": 0.0,
        "1_25": 0.13,
        "26_50": 0.38,
        "51_75": 0.63,
        "76_100": 0.88,
    }
    return mapping.get(value or "0", 0.0)
