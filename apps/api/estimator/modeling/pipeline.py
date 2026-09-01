from typing import Any

import numpy as np
import time

from estimator.modeling.benchmark import compute_benchmark_context
from estimator.modeling.complexity import compute_complexity
from estimator.modeling.confidence import compute_confidence
from estimator.modeling.format import format_currency_range, round_display_amount
from estimator.modeling.hypotheses import HYPOTHESIS_IDS
from estimator.modeling.insights import build_insights
from estimator.modeling.monte_carlo import (
    percentiles,
    rollup_hypothesis_samples,
    simulate_totals,
    theoretical_stack_p90,
)
from estimator.modeling.normalize import derive_segments, normalize_answers
from estimator.modeling.rule_posteriors import compute_posteriors, compute_rule_posteriors, get_rule_ids
from estimator.modeling.sensitivity import compute_sensitivity
from estimator.questionnaire.schema import load_hypothesis_rule_map, load_priors, load_rule_priors

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
    completion_rate: float | None = None,
) -> tuple[float, float, str]:
    low_key, high_key = SCENARIO_BANDS.get(scenario, ("p25", "p75"))
    low = pct[low_key]
    high = pct[high_key]
    effective_high_key = high_key

    if (
        scenario == "central"
        and completion_rate is not None
        and completion_rate < 0.85
        and pct["p90"] > high
    ):
        high = pct["p90"]
        effective_high_key = "p90"

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


def _build_rule_breakdown(
    per_rule: dict[str, np.ndarray],
    rule_posteriors: dict[str, float],
    rules_cfg: dict[str, dict],
    arr: float,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    raw_total = 0.0
    for rule_id, samples in per_rule.items():
        if float(np.max(samples)) <= 0:
            continue
        cfg = rules_cfg.get(rule_id, {})
        rp = percentiles(samples)
        expected_raw = float(np.mean(samples))
        if expected_raw <= 0:
            expected_raw = rp["p50"] if rp["p50"] > 0 else rp["p75"]
        if round_display_amount(expected_raw) <= 0:
            continue
        raw_total += expected_raw
        rows.append(
            {
                "rule_id": rule_id,
                "category": cfg.get("category", "unknown"),
                "leak_family": cfg.get("leak_family", "operational"),
                "hypothesis_ids": cfg.get("hypothesis_ids", []),
                "posterior_probability": rule_posteriors.get(rule_id, 0),
                "detectability": float(cfg.get("detectability", 0.7)),
                "required_entities": cfg.get("required_entities", []),
                "expected_raw": expected_raw,
                "low_raw": rp["p25"],
                "p10_raw": rp["p10"],
                "high_raw": rp["p75"],
                "p90_raw": rp["p90"],
            }
        )

    breakdown: list[dict[str, Any]] = []
    for row in rows:
        expected = round_display_amount(row["expected_raw"])
        low = round_display_amount(row["low_raw"])
        high = round_display_amount(row["high_raw"])
        if low == 0 and expected > 0:
            low = round_display_amount(row["p10_raw"])
        breakdown.append(
            {
                "rule_id": row["rule_id"],
                "category": row["category"],
                "leak_family": row["leak_family"],
                "hypothesis_ids": row["hypothesis_ids"],
                "posterior_probability": row["posterior_probability"],
                "detectability": row["detectability"],
                "required_entities": row["required_entities"],
                "expected": expected,
                "low": low,
                "high": high,
                "p90": round_display_amount(row["p90_raw"]),
                "pct_of_arr": round((row["expected_raw"] / arr) * 100, 2) if arr > 0 else 0.0,
                "likelihood": round(row["posterior_probability"] * 100, 1),
                "share_of_total": round((row["expected_raw"] / raw_total) * 100, 1) if raw_total > 0 else 0.0,
            }
        )
    breakdown.sort(key=lambda x: x["expected"], reverse=True)
    return breakdown


def _build_hypothesis_breakdown(
    per_hypothesis: dict[str, np.ndarray],
    posteriors: dict[str, float],
    rule_map: dict[str, Any],
) -> list[dict[str, Any]]:
    raw_rows: list[dict[str, Any]] = []
    raw_total = 0.0
    for hid in HYPOTHESIS_IDS:
        samples = per_hypothesis[hid]
        if float(np.max(samples)) <= 0:
            continue
        hp = percentiles(samples)
        expected_raw = float(np.mean(samples))
        if expected_raw <= 0:
            expected_raw = hp["p50"] if hp["p50"] > 0 else hp["p75"]
        if round_display_amount(expected_raw) <= 0:
            continue
        raw_total += expected_raw
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

    breakdown: list[dict[str, Any]] = []
    for row in raw_rows:
        expected = round_display_amount(row["expected_raw"])
        low = round_display_amount(row["low_raw"])
        high = round_display_amount(row["high_raw"])
        if low == 0 and expected > 0:
            low = round_display_amount(row["p10_raw"])
        if high == 0 and expected > 0:
            high = expected
        breakdown.append(
            {
                "hypothesis_id": row["hypothesis_id"],
                "name": row["name"],
                "rule_ids": row["rule_ids"],
                "posterior_probability": row["posterior_probability"],
                "expected": expected,
                "low": low,
                "mid": expected,
                "high": high,
                "pct_of_arr": 0.0,
                "likelihood": round(row["posterior_probability"] * 100, 1),
                "share_of_total": 0.0,
            }
        )
    for item in breakdown:
        if raw_total > 0:
            item["share_of_total"] = round((item["expected"] / raw_total) * 100, 1)
    breakdown.sort(key=lambda x: x["expected"], reverse=True)
    arr_ref = raw_total
    for item in breakdown:
        if arr_ref > 0:
            item["pct_of_arr"] = round((item["expected"] / arr_ref) * 100, 2)
    return breakdown


def _build_display_rollups(
    rule_breakdown: list[dict[str, Any]],
    display_rollups: dict[str, Any],
) -> list[dict[str, Any]]:
    by_rule = {row["rule_id"]: row for row in rule_breakdown}
    rollups: list[dict[str, Any]] = []
    for rollup_id, meta in display_rollups.items():
        expected = sum(by_rule[rid]["expected"] for rid in meta.get("rule_ids", []) if rid in by_rule)
        if expected <= 0:
            continue
        rollups.append(
            {
                "rollup_id": rollup_id,
                "name": meta.get("name", rollup_id),
                "rule_ids": meta.get("rule_ids", []),
                "expected": expected,
            }
        )
    rollups.sort(key=lambda x: x["expected"], reverse=True)
    return rollups


def run_model(
    answers: dict[str, Any],
    *,
    random_seed: int = 42,
    simulation_count: int | None = None,
    scenario: str = "aggressive",
    include_sensitivity: bool = True,
    completion_rate: float | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    priors = load_priors()
    rule_priors = load_rule_priors()
    sim_count = simulation_count or int(priors.get("simulation_count", 10000))

    normalized = normalize_answers(answers)
    segments = derive_segments(normalized)
    complexity = compute_complexity(normalized)
    normalized["complexity.total"] = complexity["total"]
    rule_posteriors = compute_rule_posteriors(normalized, rule_priors)
    posteriors = compute_posteriors(normalized, priors)
    rng = np.random.default_rng(random_seed)
    arr = segments["arr"]
    rules_cfg = rule_priors.get("rules", {})

    totals, gross_totals, detectable, recoverable, per_rule, per_recoverable = simulate_totals(
        rng,
        arr,
        segments,
        rule_posteriors,
        priors,
        rule_priors,
        sim_count,
        complexity["total"],
        normalized,
    )
    per_hypothesis = rollup_hypothesis_samples(per_rule, rules_cfg)
    pct = percentiles(totals)
    det_pct = percentiles(detectable)
    rec_pct = percentiles(recoverable)
    sim_stats_raw = _simulation_stats(totals)
    gross_mean = float(np.mean(gross_totals))
    expected_mean = sim_stats_raw["expected_mean"]
    stack_p90 = theoretical_stack_p90(per_rule)

    estimate_low_raw, estimate_high_raw, high_band_key = _scenario_bounds(
        pct, scenario, expected_mean=expected_mean, completion_rate=completion_rate
    )
    det_low_raw, det_high_raw, _ = _scenario_bounds(
        det_pct, scenario, expected_mean=float(np.mean(detectable)), completion_rate=completion_rate
    )

    rule_map_data = load_hypothesis_rule_map()
    hypothesis_meta = rule_map_data.get("hypotheses", {})
    rule_breakdown = _build_rule_breakdown(per_rule, rule_posteriors, rules_cfg, arr)
    hypothesis_breakdown = _build_hypothesis_breakdown(per_hypothesis, posteriors, hypothesis_meta)
    display_rollups = _build_display_rollups(
        rule_breakdown, rule_map_data.get("display_rollups", {})
    )

    for item in hypothesis_breakdown:
        if arr > 0:
            item["pct_of_arr"] = round((item["expected"] / arr) * 100, 2)

    confidence = compute_confidence(normalized, complexity, answers)
    sensitivity = (
        compute_sensitivity(normalized, posteriors, priors, segments, answers)
        if include_sensitivity
        else []
    )

    estimate_low = round_display_amount(estimate_low_raw)
    estimate_high = round_display_amount(estimate_high_raw)
    estimate_central = round_display_amount(expected_mean)
    gross_expected = round_display_amount(gross_mean)
    net_recoverable = estimate_central
    median_run = round_display_amount(sim_stats_raw["median_run"])
    recoverable_expected = round_display_amount(float(np.mean(recoverable)))
    at_risk_expected = max(estimate_central - recoverable_expected, 0)
    stress_p90 = round_display_amount(pct["p90"])
    stack_p90_rounded = round_display_amount(stack_p90)
    overlap_discount = max(stack_p90_rounded - estimate_central, 0)
    arr_uncertainty = float(normalized.get("arr_uncertainty", 0.05))
    arr_band_low = round_display_amount(expected_mean * (1 - arr_uncertainty))
    arr_band_high = round_display_amount(expected_mean * (1 + arr_uncertainty))

    estimate = {
        "low": estimate_low,
        "central": estimate_central,
        "high": estimate_high,
        "median_run": median_run,
        "display_range": format_currency_range(estimate_low, estimate_high),
        "stress_p90": stress_p90,
        "theoretical_stack_p90": stack_p90_rounded,
        "recoverable": recoverable_expected,
        "at_risk": at_risk_expected,
        "overlap_discount": overlap_discount,
        "arr_band_low": arr_band_low,
        "arr_band_high": arr_band_high,
        "gross_expected": gross_expected,
        "net_recoverable": net_recoverable,
    }

    benchmark_context = compute_benchmark_context(
        arr,
        complexity.get("label", "Low"),
        estimate_central,
        priors,
    )

    display_headline_usd = estimate_high
    if benchmark_context and benchmark_context.get("may_understate"):
        display_headline_usd = max(estimate_high, benchmark_context["low_usd"])
    estimate["display_headline_usd"] = display_headline_usd

    sim_stats = {
        "expected_mean": estimate_central,
        "median_run": median_run,
        "pct_runs_with_leakage": round(sim_stats_raw["pct_runs_with_leakage"], 1),
        "conditional_mean": round_display_amount(sim_stats_raw["conditional_mean"]),
        "gross_expected": gross_expected,
        "net_recoverable": net_recoverable,
        "high_band_key": high_band_key,
        "stress_p90": stress_p90,
        "theoretical_stack_p90": stack_p90_rounded,
        "recoverable_expected": recoverable_expected,
        "at_risk_expected": at_risk_expected,
    }

    insights = build_insights(
        normalized=normalized,
        segments=segments,
        complexity=complexity,
        top_hypotheses=hypothesis_breakdown[:5],
        rule_breakdown=rule_breakdown,
        estimate=estimate,
        detectable={
            "low": round_display_amount(det_low_raw),
            "high": round_display_amount(det_high_raw),
        },
        arr=arr,
        priors=priors,
        rule_priors=rule_priors,
        sim_stats=sim_stats,
        scenario=scenario,
        scenario_band=SCENARIO_BANDS.get(scenario, ("p25", "p75")),
        simulation_count=sim_count,
    )

    runtime_ms = int((time.perf_counter() - started) * 1000)

    return {
        "estimate": estimate,
        "benchmark_context": benchmark_context,
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
        "recoverable": {
            "expected": recoverable_expected,
            "low": round_display_amount(rec_pct["p25"]),
            "high": round_display_amount(rec_pct["p75"]),
        },
        "theoretical_stack": {
            "p90": stack_p90_rounded,
            "overlap_discount": overlap_discount,
        },
        "confidence": confidence,
        "complexity": complexity,
        "top_hypotheses": hypothesis_breakdown[:5],
        "hypothesis_breakdown": hypothesis_breakdown,
        "rule_breakdown": rule_breakdown,
        "display_rollups": display_rollups,
        "drivers": sensitivity[:5],
        "sensitivity": sensitivity,
        "segments": segments,
        "posteriors": posteriors,
        "rule_posteriors": rule_posteriors,
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
            "value": "rule_native_v2",
            "unit": None,
            "source": "model_prior",
            "type": "prior",
            "version": priors.get("version", "1.0.0"),
            "confidence": "low",
        },
    ]
