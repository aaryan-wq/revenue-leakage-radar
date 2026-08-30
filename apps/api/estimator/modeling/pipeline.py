from typing import Any

from estimator.modeling.complexity import compute_complexity
from estimator.modeling.hypotheses import HYPOTHESIS_IDS, compute_posteriors
from estimator.modeling.monte_carlo import percentiles, simulate_totals
from estimator.modeling.normalize import derive_segments, normalize_answers
from estimator.questionnaire.schema import load_hypothesis_rule_map, load_priors
from estimator.modeling.format import format_currency_range, round_display_amount
from estimator.modeling.sensitivity import compute_sensitivity
from estimator.modeling.confidence import compute_confidence
import numpy as np
import time


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
    scenario_multiplier = {"conservative": 0.75, "central": 1.0, "aggressive": 1.25}.get(scenario, 1.0)

    normalized = normalize_answers(answers)
    segments = derive_segments(normalized)
    complexity = compute_complexity(normalized)
    posteriors = compute_posteriors(normalized, priors)
    rng = np.random.default_rng(random_seed)
    arr = segments["arr"]

    totals, detectable, per_hyp = simulate_totals(
        rng, arr, segments, posteriors, priors, sim_count, scenario_multiplier
    )
    pct = percentiles(totals)
    det_pct = percentiles(detectable)

    hypothesis_breakdown = []
    rule_map = load_hypothesis_rule_map()["hypotheses"]
    for hid in HYPOTHESIS_IDS:
        samples = per_hyp[hid]
        if float(np.max(samples)) <= 0:
            continue
        hp = percentiles(samples)
        meta = rule_map.get(hid, {})
        hypothesis_breakdown.append(
            {
                "hypothesis_id": hid,
                "name": meta.get("name", hid),
                "rule_ids": meta.get("rule_ids", []),
                "posterior_probability": posteriors.get(hid, 0),
                "low": round_display_amount(hp["p25"]),
                "mid": round_display_amount(hp["p50"]),
                "high": round_display_amount(hp["p75"]),
            }
        )
    hypothesis_breakdown.sort(key=lambda x: x["mid"], reverse=True)

    confidence = compute_confidence(normalized, complexity, answers)
    sensitivity = compute_sensitivity(normalized, posteriors, priors, segments)

    runtime_ms = int((time.perf_counter() - started) * 1000)
    estimate_low = round_display_amount(pct["p25"])
    estimate_high = round_display_amount(pct["p75"])

    return {
        "estimate": {
            "low": estimate_low,
            "central": round_display_amount(pct["p50"]),
            "high": estimate_high,
            "display_range": format_currency_range(estimate_low, estimate_high),
        },
        "monthly": {
            "low": round_display_amount(pct["p25"] / 12),
            "central": round_display_amount(pct["p50"] / 12),
            "high": round_display_amount(pct["p75"] / 12),
        },
        "percentiles": {k: round_display_amount(v) for k, v in pct.items()},
        "detectable": {
            "low": round_display_amount(det_pct["p25"]),
            "high": round_display_amount(det_pct["p75"]),
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
        "runtime_ms": runtime_ms,
        "what_would_need_to_be_true": _what_would_need_to_be_true(hypothesis_breakdown[:3]),
        "arr_usd": arr,
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


def _what_would_need_to_be_true(top: list[dict]) -> list[str]:
    statements = []
    for item in top:
        statements.append(f"A portion of revenue may be exposed to {item['name'].lower()}.")
    if not statements:
        statements.append("Multiple minor billing configuration gaps may compound across your customer base.")
    return statements
