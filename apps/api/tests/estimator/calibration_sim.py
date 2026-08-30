"""Monte Carlo simulator for calibration tuning."""

from __future__ import annotations

import numpy as np

from estimator.modeling.hypotheses import HYPOTHESIS_IDS, compute_posteriors
from estimator.modeling.monte_carlo import apply_correlation_adjustment
from estimator.modeling.normalize import derive_segments, normalize_answers
from estimator.questionnaire.schema import load_priors


def simulate(
    answers: dict,
    *,
    seed: int = 42,
    affected: tuple[int, int] = (2, 20),
    persistence_divisor: float = 12.0,
    leakage_scale: float = 1.0,
    use_posterior_gate: bool = True,
) -> float:
    priors = load_priors()
    normalized = normalize_answers(answers)
    segments = derive_segments(normalized)
    posteriors = compute_posteriors(normalized, priors)
    rng = np.random.default_rng(seed)
    arr = segments["arr"]
    hypothesis_cfg = priors["hypotheses"]
    correlations = priors.get("correlations", {})
    max_fraction = float(priors.get("max_leakage_fraction_of_arr", 0.35))

    base_map = {
        "arr": segments["arr"],
        "contract_arr": segments["contract_arr"],
        "discount_arr": segments["discount_arr"],
        "usage_arr": segments["usage_arr"],
        "seat_arr": segments["seat_arr"],
        "addon_arr": segments["addon_arr"],
        "international_arr": segments["international_arr"],
    }

    totals = np.zeros(10_000)
    for sim in range(10_000):
        amounts: dict[str, float] = {}
        for hid in HYPOTHESIS_IDS:
            cfg = hypothesis_cfg.get(hid, {})
            posterior = posteriors.get(hid, 0.05)
            if use_posterior_gate and rng.random() > posterior:
                continue
            exposure_base = float(base_map.get(cfg.get("exposure_base", "arr"), arr))
            if exposure_base <= 0:
                continue
            affected_draw = rng.beta(affected[0], affected[1])
            sev_cfg = cfg.get("severity", {})
            severity = rng.beta(sev_cfg.get("alpha", 2), sev_cfg.get("beta", 6))
            pers_cfg = cfg.get("persistence", {})
            persistence = rng.gamma(pers_cfg.get("shape", 2), pers_cfg.get("scale", 3)) / persistence_divisor
            rec_cfg = cfg.get("recoverability", {})
            recoverability = rng.beta(rec_cfg.get("alpha", 3), rec_cfg.get("beta", 4))
            multiplier = 1.0 if use_posterior_gate else posterior
            leakage = (
                exposure_base
                * affected_draw
                * severity
                * persistence
                * recoverability
                * multiplier
                * leakage_scale
            )
            amounts[hid] = leakage
        adjusted, _ = apply_correlation_adjustment(amounts, correlations)
        totals[sim] = min(adjusted, arr * max_fraction)
    return float(np.mean(totals))
