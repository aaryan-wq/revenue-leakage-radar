"""Grid search estimator priors against audit-derived calibration cases."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

import yaml

from calibration.cases import AuditCalibrationCase
from calibration.compare import ComparisonRow, max_abs_error, mean_abs_error
from estimator.modeling.pipeline import run_model
from estimator.questionnaire.schema import load_audit_calibration, load_priors, load_rule_priors

API_ROOT = Path(__file__).resolve().parents[1]
PRIORS_PATH = API_ROOT / "estimator" / "schema" / "model" / "v1.0" / "priors.yaml"
AUDIT_CALIBRATION_PATH = API_ROOT / "estimator" / "schema" / "model" / "v1.0" / "audit-calibration.yaml"


@dataclass
class TuneConfig:
    complexity_base: float = 2.05
    affected_beta: int = 9
    rule_prior_multiplier: float = 1.0


@dataclass
class TuneResult:
    mean_abs_error_pct: float
    max_abs_error_pct: float
    config: TuneConfig
    rows: list


def _clear_schema_caches() -> None:
    load_priors.cache_clear()
    load_rule_priors.cache_clear()
    load_audit_calibration.cache_clear()


def _load_overlay_multipliers() -> dict[str, float]:
    data = load_audit_calibration()
    raw = data.get("rule_prior_multipliers") or {}
    return {str(rule_id): float(value) for rule_id, value in raw.items()}


def _apply_tune_config(config: TuneConfig) -> tuple[Callable, Callable]:
    base_priors = copy.deepcopy(load_priors())
    base_rule_priors = copy.deepcopy(load_rule_priors())

    base_priors.setdefault("monte_carlo", {}).setdefault("complexity_scale", {})["base"] = config.complexity_base
    base_priors.setdefault("monte_carlo", {}).setdefault("affected_rate", {})["beta"] = config.affected_beta

    if config.rule_prior_multiplier != 1.0:
        for rule_cfg in base_rule_priors.get("rules", {}).values():
            rule_cfg["prior"] = float(rule_cfg.get("prior", 0.03)) * config.rule_prior_multiplier

    def patched_load_priors(version: str = "1.0") -> dict[str, Any]:
        return copy.deepcopy(base_priors)

    def patched_load_rule_priors(version: str = "1.0") -> dict[str, Any]:
        return copy.deepcopy(base_rule_priors)

    return patched_load_priors, patched_load_rule_priors


def score_cases(cases: list[AuditCalibrationCase], config: TuneConfig, *, random_seed: int = 42) -> TuneResult:
    patched_priors, patched_rule_priors = _apply_tune_config(config)
    _clear_schema_caches()

    import estimator.modeling.pipeline as pipeline
    import estimator.modeling.rule_posteriors as rule_posteriors
    import estimator.questionnaire.schema as schema

    original_priors = schema.load_priors
    original_rule_priors = schema.load_rule_priors
    schema.load_priors = patched_priors  # type: ignore[assignment]
    schema.load_rule_priors = patched_load_rule_priors  # type: ignore[assignment]
    pipeline.load_priors = patched_priors  # type: ignore[assignment]
    pipeline.load_rule_priors = patched_load_rule_priors  # type: ignore[assignment]
    rule_posteriors.load_rule_priors = patched_load_rule_priors  # type: ignore[assignment]

    rows: list[ComparisonRow] = []
    try:
        from calibration.compare import compare_case

        for case in cases:
            row, _ = compare_case(case, random_seed=random_seed)
            rows.append(row)
    finally:
        schema.load_priors = original_priors  # type: ignore[assignment]
        schema.load_rule_priors = original_rule_priors  # type: ignore[assignment]
        pipeline.load_priors = original_priors  # type: ignore[assignment]
        pipeline.load_rule_priors = original_rule_priors  # type: ignore[assignment]
        rule_posteriors.load_rule_priors = original_rule_priors  # type: ignore[assignment]
        _clear_schema_caches()

    return TuneResult(
        mean_abs_error_pct=mean_abs_error(rows),
        max_abs_error_pct=max_abs_error(rows),
        config=config,
        rows=rows,
    )


def grid_search(
    cases: list[AuditCalibrationCase],
    *,
    random_seed: int = 42,
    config: TuneConfig | None = None,
    fast: bool = False,
) -> TuneResult:
    base = config or TuneConfig()
    if fast:
        complexity_values = [base.complexity_base, 2.0, 2.1, 2.2]
        beta_values = [max(base.affected_beta - 1, 5), base.affected_beta, base.affected_beta + 1]
        rule_mult_values = [1.0]
    else:
        complexity_values = _neighbor_values(base.complexity_base, [1.8, 2.0, 2.05, 2.1, 2.2, 2.4])
        beta_values = _neighbor_values(float(base.affected_beta), [7, 9, 11])
        rule_mult_values = _neighbor_values(base.rule_prior_multiplier, [0.9, 1.0, 1.1])

    best = TuneResult(mean_abs_error_pct=999.0, max_abs_error_pct=999.0, config=base, rows=[])
    for complexity_base in complexity_values:
        for affected_beta in beta_values:
            for rule_mult in rule_mult_values:
                candidate = TuneConfig(
                    complexity_base=complexity_base,
                    affected_beta=int(affected_beta),
                    rule_prior_multiplier=rule_mult,
                )
                result = score_cases(cases, candidate, random_seed=random_seed)
                if result.mean_abs_error_pct < best.mean_abs_error_pct:
                    best = result
    return best


def _neighbor_values(center: float, grid: list[float]) -> list[float]:
    band = [value for value in grid if abs(value - center) <= 0.35 or abs(value - center) <= 2.5]
    return sorted(set(band or grid))


def apply_config_to_priors(config: TuneConfig) -> None:
    priors_text = PRIORS_PATH.read_text(encoding="utf-8")
    priors_text = re.sub(
        r"(complexity_scale:\n\s+base:\s+)[0-9.]+",
        rf"\g<1>{config.complexity_base}",
        priors_text,
        count=1,
    )
    priors_text = re.sub(
        r"(affected_rate:\n\s+alpha:\s+[0-9]+\n\s+beta:\s+)[0-9]+",
        rf"\g<1>{config.affected_beta}",
        priors_text,
        count=1,
    )
    PRIORS_PATH.write_text(priors_text, encoding="utf-8")
    _clear_schema_caches()


def compute_rule_prior_adjustments(
    cases: list[AuditCalibrationCase],
    rows: list[ComparisonRow],
    *,
    damping: float = 0.5,
) -> dict[str, float]:
    """Return rule_id -> multiplicative overlay adjustment from audit/estimator rule-level ratios."""
    existing = _load_overlay_multipliers()
    buckets: dict[str, list[float]] = {}
    for case, row in zip(cases, rows):
        if len(case.injected_rules) != 1:
            continue
        rule_id = case.injected_rules[0]
        audit = row.audit_target_usd
        estimate = row.estimator_rule_usd if row.estimator_rule_usd > 0 else row.estimator_central_usd
        if audit <= 0 or estimate <= 0:
            continue
        ratio = audit / estimate
        damped = ratio**damping
        buckets.setdefault(rule_id, []).append(damped)

    adjustments: dict[str, float] = {}
    for rule_id, values in buckets.items():
        values = sorted(values)
        median = values[len(values) // 2]
        prior = existing.get(rule_id, 1.0)
        adjustments[rule_id] = min(max(prior * median, 0.05), 4.0)
    return adjustments


def write_audit_calibration_overlay(adjustments: dict[str, float], *, stage: int = 1) -> None:
    payload = {
        "version": 1,
        "calibration_stage": stage,
        "source": "audit_driven_loop",
        "rule_prior_multipliers": {rule_id: round(value, 6) for rule_id, value in sorted(adjustments.items())},
    }
    AUDIT_CALIBRATION_PATH.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")
    _clear_schema_caches()


def _apply_overlay_to_rule_priors(rule_priors: dict[str, Any], multipliers: dict[str, float]) -> dict[str, Any]:
    data = copy.deepcopy(rule_priors)
    for rule_id, multiplier in multipliers.items():
        if multiplier == 1.0:
            continue
        rule_cfg = data.get("rules", {}).get(rule_id)
        if not rule_cfg:
            continue
        base_prior = float(rule_cfg.get("prior", 0.03))
        rule_cfg["prior"] = min(max(base_prior * float(multiplier), 0.001), 0.5)
    return data


def _with_overlay_multipliers(multipliers: dict[str, float]):
    """Patch rule priors loader to include audit-calibration overlay multipliers."""
    import estimator.modeling.pipeline as pipeline
    import estimator.modeling.rule_posteriors as rule_posteriors
    import estimator.questionnaire.schema as schema

    base_rule_priors = schema.load_rule_priors()
    overlaid = _apply_overlay_to_rule_priors(base_rule_priors, multipliers)

    def patched_load_rule_priors(version: str = "1.0") -> dict[str, Any]:
        return copy.deepcopy(overlaid)

    original_rule_priors = schema.load_rule_priors
    schema.load_rule_priors = patched_load_rule_priors  # type: ignore[assignment]
    pipeline.load_rule_priors = patched_load_rule_priors  # type: ignore[assignment]
    rule_posteriors.load_rule_priors = patched_load_rule_priors  # type: ignore[assignment]
    return schema, pipeline, rule_posteriors, original_rule_priors


def _restore_overlay_patch(schema, pipeline, rule_posteriors, original_rule_priors) -> None:
    schema.load_rule_priors = original_rule_priors  # type: ignore[assignment]
    pipeline.load_rule_priors = original_rule_priors  # type: ignore[assignment]
    rule_posteriors.load_rule_priors = original_rule_priors  # type: ignore[assignment]
    _clear_schema_caches()


def calibration_fixtures_pass_with_overlay(multipliers: dict[str, float]) -> bool:
    from estimator.modeling.pipeline import run_model
    from tests.estimator.calibration_fixtures import CALIBRATION_CASES

    schema, pipeline, rule_posteriors, original_rule_priors = _with_overlay_multipliers(multipliers)
    try:
        errors: list[float] = []
        for case in CALIBRATION_CASES:
            result = run_model(case["answers"], random_seed=42, include_sensitivity=False)
            model = result["estimate"]["central"]
            justified = case["justified_leakage_usd"]
            errors.append(abs((model - justified) / justified * 100))
        mean_error = sum(errors) / len(errors)
        max_error = max(errors)
        return mean_error <= 12.0 and max_error <= 26.0
    finally:
        _restore_overlay_patch(schema, pipeline, rule_posteriors, original_rule_priors)


def calibration_fixtures_pass() -> bool:
    return calibration_fixtures_pass_with_overlay(_load_overlay_multipliers())


def safe_apply_rule_overlay(adjustments: dict[str, float]) -> tuple[int, bool]:
    """Apply overlay multipliers one rule at a time, keeping only fixture-safe changes."""
    if not adjustments:
        return 0, True
    merged = dict(_load_overlay_multipliers())
    applied = 0
    for rule_id, multiplier in sorted(adjustments.items()):
        trial = dict(merged)
        trial[rule_id] = multiplier
        if calibration_fixtures_pass_with_overlay(trial):
            merged = trial
            applied += 1
    write_audit_calibration_overlay(merged)
    return applied, applied > 0 or not adjustments


def iterative_search(
    cases: list[AuditCalibrationCase],
    *,
    iterations: int = 3,
    random_seed: int = 42,
) -> TuneResult:
    best = grid_search(cases, random_seed=random_seed)
    for _ in range(max(iterations - 1, 0)):
        candidate = grid_search(cases, random_seed=random_seed, config=best.config)
        if candidate.mean_abs_error_pct < best.mean_abs_error_pct:
            best = candidate
    return best
