import numpy as np

from estimator.modeling.hypotheses import HYPOTHESIS_IDS


def apply_correlation_adjustment(
    hypothesis_amounts: dict[str, float],
    correlations: dict[str, dict[str, float]],
) -> tuple[float, dict[str, float]]:
    raw_total = sum(hypothesis_amounts.values())
    penalty = 0.0
    pair_penalties: dict[str, float] = {}

    for i, hi in enumerate(HYPOTHESIS_IDS):
        li = hypothesis_amounts.get(hi, 0.0)
        if li <= 0:
            continue
        corr_row = correlations.get(hi, {})
        for hj in HYPOTHESIS_IDS[i + 1 :]:
            rho = corr_row.get(hj) or correlations.get(hj, {}).get(hi)
            if not rho:
                continue
            lj = hypothesis_amounts.get(hj, 0.0)
            if lj <= 0:
                continue
            overlap = rho * min(li, lj) * 0.5
            penalty += overlap
            pair_penalties[f"{hi}:{hj}"] = overlap

    adjusted = max(raw_total - penalty, 0.0)
    return adjusted, pair_penalties


def simulate_totals(
    rng: np.random.Generator,
    arr: float,
    segments: dict[str, float],
    posteriors: dict[str, float],
    priors: dict,
    simulation_count: int,
) -> tuple[np.ndarray, np.ndarray, dict[str, np.ndarray]]:
    hypothesis_cfg = priors["hypotheses"]
    correlations = priors.get("correlations", {})
    max_fraction = float(priors.get("max_leakage_fraction_of_arr", 0.35))
    totals = np.zeros(simulation_count)
    detectable = np.zeros(simulation_count)
    per_hypothesis: dict[str, np.ndarray] = {hid: np.zeros(simulation_count) for hid in HYPOTHESIS_IDS}

    base_map = {
        "arr": segments["arr"],
        "contract_arr": segments["contract_arr"],
        "discount_arr": segments["discount_arr"],
        "usage_arr": segments["usage_arr"],
        "seat_arr": segments["seat_arr"],
        "addon_arr": segments["addon_arr"],
        "international_arr": segments["international_arr"],
    }

    for sim in range(simulation_count):
        amounts: dict[str, float] = {}
        for hid in HYPOTHESIS_IDS:
            cfg = hypothesis_cfg.get(hid, {})
            posterior = posteriors.get(hid, 0.05)
            if rng.random() > posterior:
                continue
            exposure_base = float(base_map.get(cfg.get("exposure_base", "arr"), arr))
            if exposure_base <= 0:
                continue
            affected = rng.beta(2, 20)
            sev_cfg = cfg.get("severity", {})
            severity = rng.beta(sev_cfg.get("alpha", 2), sev_cfg.get("beta", 6))
            pers_cfg = cfg.get("persistence", {})
            persistence = rng.gamma(pers_cfg.get("shape", 2), pers_cfg.get("scale", 3)) / 12.0
            rec_cfg = cfg.get("recoverability", {})
            recoverability = rng.beta(rec_cfg.get("alpha", 3), rec_cfg.get("beta", 4))
            detectability = float(cfg.get("detectability", 0.7))
            leakage = exposure_base * affected * severity * persistence * recoverability
            amounts[hid] = leakage
            per_hypothesis[hid][sim] = leakage

        adjusted, _ = apply_correlation_adjustment(amounts, correlations)
        capped = min(adjusted, arr * max_fraction)
        totals[sim] = capped
        detectable[sim] = capped * np.mean([float(hypothesis_cfg.get(h, {}).get("detectability", 0.7)) for h in amounts]) if amounts else 0.0

    return totals, detectable, per_hypothesis


def percentiles(values: np.ndarray) -> dict[str, float]:
    return {
        "p10": float(np.percentile(values, 10)),
        "p25": float(np.percentile(values, 25)),
        "p50": float(np.percentile(values, 50)),
        "p75": float(np.percentile(values, 75)),
        "p90": float(np.percentile(values, 90)),
    }
