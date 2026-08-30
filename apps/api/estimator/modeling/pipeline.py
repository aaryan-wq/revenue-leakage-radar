from typing import Any

import numpy as np
import time

from estimator.modeling.complexity import compute_complexity
from estimator.modeling.confidence import compute_confidence
from estimator.modeling.format import format_currency_range, round_display_amount
from estimator.modeling.hypotheses import HYPOTHESIS_IDS, compute_posteriors
from estimator.modeling.insights import build_insights
from estimator.modeling.monte_carlo import percentiles, simulate_totals
from estimator.modeling.normalize import derive_segments, normalize_answers
from estimator.modeling.sensitivity import compute_sensitivity
from estimator.questionnaire.schema import load_hypothesis_rule_map, load_priors

SCENARIO_BANDS: dict[str, tuple[str, str]] = {
    "conservative": ("p10", "p50"),
    "central": ("p25", "p75"),
    "aggressive": ("p50", "p90"),
}


def _simulation_stats(totals: np.ndarray) -> dict[str, float]:
    nonzero = totals[totals > 0]
    return {
        "expected_mean": float(np.mean(totals)),
        "median_run": float(np.percentile(totals, 50)),
        "pct_runs_with_leakage": float(len(nonzero) / len(totals) * 100) if len(totals) else 0.0,
        "conditional_mean": float(np.mean(nonzero)) if len(nonzero) else 0.0,
    }


def _scenario_bounds(
    pct: dict[str, float],
    scenario: str,
    *,
    expected_mean: float,
) -> tuple[float, float, str]:
    low_key, high_key = SCENARIO_BANDS.get(scenario, ("p25", "p75"))
    low = pct[low_key]
    high = pct[high_key]
    effective_high_key = high_key

    expected_rounded = round_display_amount(expected_mean)
    median_rounded = round_display_amount(pct["p50"])

    if scenario == "central" and expected_rounded > 0 and round_display_amount(high) < expected_rounded:
        high = pct["p90"]
        effective_high_key = "p90"

    if expected_rounded > 0 and round_display_amount(low) == 0:
        if median_rounded > 0:
            low = pct["p50"]
        elif round_display_amount(pct["p10"]) > 0:
            low = pct["p10"]

    if round_display_amount(high) < expected_rounded:
        high = max(high, expected_mean)

    if round_display_amount(low) > round_display_amount(high):
        low = high

    return low, high, effective_high_key


def run_model(
    answers: dict[str, Any],
    *,
    random_seed: int = 42,
    simulation_count: int | None = None,
    scenario: str = "central",
) -> dict[str, Any]:
    started = time.perf_counter()
    priors = load_priors()
    sim_count = simulation_count or int(priors.get("simulation_count", 10000))

    normalized = normalize_answers(answers)
    segments = derive_segments(normalized)
    complexity = compute_complexity(normalized)
    posteriors = compute_posteriors(normalized, priors)
    rng = np.random.default_rng(random_seed)
    arr = segments["arr"]

    totals, detectable, per_hyp = simulate_totals(
        rng, arr, segments, posteriors, priors, sim_count, complexity["total"]
    )
    pct = percentiles(totals)
    det_pct = percentiles(detectable)
    sim_stats_raw = _simulation_stats(totals)
    expected_mean = sim_stats_raw["expected_mean"]

    estimate_low_raw, estimate_high_raw, high_band_key = _scenario_bounds(
        pct, scenario, expected_mean=expected_mean
    )
    det_low_raw, det_high_raw, _ = _scenario_bounds(det_pct, scenario, expected_mean=float(np.mean(detectable)))

    hypothesis_breakdown = []
    rule_map = load_hypothesis_rule_map()["hypotheses"]
    raw_p50_total = 0.0
    raw_rows: list[dict[str, Any]] = []

    for hid in HYPOTHESIS_IDS:
        samples = per_hyp[hid]
        if float(np.max(samples)) <= 0:
            continue
        hp = percentiles(samples)
        expected_raw = float(np.mean(samples))
        if expected_raw <= 0:
            expected_raw = hp["p50"] if hp["p50"] > 0 else hp["p75"]
        if round_display_amount(expected_raw) <= 0:
            continue
        raw_p50_total += expected_raw
        meta = rule_map.get(hid, {})
        raw_rows.append(
            {
                "hypothesis_id": hid,
                "name": meta.get("name", hid),
                "rule_ids": meta.get("rule_ids", []),
                "posterior_probability": posteriors.get(hid, 0),
                "expected_raw": expected_raw,
                "low_raw": hp["p25"],
                "p10_raw": hp["p10"],
                "high_raw": hp["p75"],
            }
        )

    for row in raw_rows:
        expected = round_display_amount(row["expected_raw"])
        low = round_display_amount(row["low_raw"])
        high = round_display_amount(row["high_raw"])
        if low == 0 and expected > 0:
            low = round_display_amount(row["p10_raw"])
        likelihood = round(row["posterior_probability"] * 100, 1)
        pct_of_arr = round((row["expected_raw"] / arr) * 100, 2) if arr > 0 else 0.0
        share_of_total = round((row["expected_raw"] / raw_p50_total) * 100, 1) if raw_p50_total > 0 else 0.0
        hypothesis_breakdown.append(
            {
                "hypothesis_id": row["hypothesis_id"],
                "name": row["name"],
                "rule_ids": row["rule_ids"],
                "posterior_probability": row["posterior_probability"],
                "expected": expected,
                "low": low,
                "mid": expected,
                "high": high,
                "pct_of_arr": pct_of_arr,
                "likelihood": likelihood,
                "share_of_total": share_of_total,
            }
        )
    hypothesis_breakdown.sort(key=lambda x: x["expected"], reverse=True)

    confidence = compute_confidence(normalized, complexity, answers)
    sensitivity = compute_sensitivity(normalized, posteriors, priors, segments)

    estimate_low = round_display_amount(estimate_low_raw)
    estimate_high = round_display_amount(estimate_high_raw)
    estimate_central = round_display_amount(expected_mean)
    median_run = round_display_amount(sim_stats_raw["median_run"])

    estimate = {
        "low": estimate_low,
        "central": estimate_central,
        "high": estimate_high,
        "median_run": median_run,
        "display_range": format_currency_range(estimate_low, estimate_high),
    }

    sim_stats = {
        "expected_mean": estimate_central,
        "median_run": median_run,
        "pct_runs_with_leakage": round(sim_stats_raw["pct_runs_with_leakage"], 1),
        "conditional_mean": round_display_amount(sim_stats_raw["conditional_mean"]),
        "high_band_key": high_band_key,
    }

    insights = build_insights(
        normalized=normalized,
        segments=segments,
        complexity=complexity,
        top_hypotheses=hypothesis_breakdown[:5],
        estimate=estimate,
        detectable={
            "low": round_display_amount(det_low_raw),
            "high": round_display_amount(det_high_raw),
        },
        arr=arr,
        priors=priors,
        sim_stats=sim_stats,
        scenario=scenario,
        scenario_band=SCENARIO_BANDS.get(scenario, ("p25", "p75")),
        simulation_count=sim_count,
    )

    runtime_ms = int((time.perf_counter() - started) * 1000)

    return {
        "estimate": estimate,
        "monthly": {
            "low": round_display_amount(estimate_low_raw / 12),
            "central": round_display_amount(expected_mean / 12),
            "high": round_display_amount(estimate_high_raw / 12),
        },
        "percentiles": {k: round_display_amount(v) for k, v in pct.items()},
        "detectable": {
            "low": round_display_amount(det_low_raw),
            "high": round_display_amount(det_high_raw),
        },
        "confidence": confidence,
        "complexity": complexity,
        "top_hypotheses": hypothesis_breakdown[:5],
        "hypothesis_breakdown": hypothesis_breakdown,
        "drivers": sensitivity[:5],
        "sensitivity": sensitivity,
        "segments": segments,
        "posteriors": posteriors,
        "assumptions": _build_assumptions(normalized, priors),
        "model_version": priors.get("version", "1.0.0"),
        "calibration_stage": priors.get("calibration_stage", 0),
        "random_seed": random_seed,
        "simulation_count": sim_count,
        "scenario": scenario,
        "scenario_band": SCENARIO_BANDS.get(scenario, ("p25", "p75")),
        "runtime_ms": runtime_ms,
        "arr_usd": arr,
        **insights,
    }


def _build_assumptions(normalized: dict[str, Any], priors: dict) -> list[dict[str, str]]:
    return [
        {
            "assumption_id": "arr_usd",
            "category": "input",
            "value": str(normalized.get("arr_usd", 0)),
            "unit": "USD",
            "source": "user",
            "type": "input",
            "version": priors.get("version", "1.0.0"),
            "confidence": normalized.get("profile.arr_confidence", "approximate"),
        },
        {
            "assumption_id": "model_priors",
            "category": "model",
            "value": "structural_assumptions",
            "unit": None,
            "source": "model_prior",
            "type": "prior",
            "version": priors.get("version", "1.0.0"),
            "confidence": "low",
        },
    ]
