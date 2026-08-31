"""Grid search estimator priors against audit-derived calibration cases."""

from __future__ import annotations

import copy
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from calibration.cases import AuditCalibrationCase
from calibration.compare import ComparisonRow, max_abs_error, mean_abs_error
from estimator.modeling.pipeline import run_model
from estimator.questionnaire.schema import load_priors, load_rule_priors

PRIORS_PATH = Path(__file__).resolve().parents[1] / "estimator" / "schema" / "model" / "v1.0" / "priors.yaml"
RULE_PRIORS_PATH = (
    Path(__file__).resolve().parents[1] / "estimator" / "schema" / "model" / "v1.0" / "rule-priors.yaml"
)

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
    load_priors.cache_clear()
    load_rule_priors.cache_clear()

    import estimator.modeling.pipeline as pipeline
    import estimator.modeling.rule_posteriors as rule_posteriors
    import estimator.questionnaire.schema as schema

    original_priors = schema.load_priors
    original_rule_priors = schema.load_rule_priors
    schema.load_priors = patched_priors  # type: ignore[assignment]
    schema.load_rule_priors = patched_rule_priors  # type: ignore[assignment]
    pipeline.load_priors = patched_priors  # type: ignore[assignment]
    pipeline.load_rule_priors = patched_rule_priors  # type: ignore[assignment]
    rule_posteriors.load_rule_priors = patched_rule_priors  # type: ignore[assignment]

    rows: list[ComparisonRow] = []
    try:
        for case in cases:
            result = run_model(case.answers, random_seed=random_seed, include_sensitivity=False)
            estimator_central = float(result["estimate"]["central"])
            audit_target = case.audit_target_usd
            error_pct = ((estimator_central - audit_target) / audit_target * 100) if audit_target > 0 else 0.0
            injected = case.injected_annual_usd
            audit_vs_injected = (
                ((audit_target - injected) / injected * 100) if injected > 0 else 0.0
            )
            rows.append(
                ComparisonRow(
                    case_id=case.case_id,
                    name=case.name,
                    audit_target_usd=audit_target,
                    injected_annual_usd=injected,
                    estimator_central_usd=estimator_central,
                    error_pct=error_pct,
                    abs_error_pct=abs(error_pct),
                    audit_vs_injected_pct=audit_vs_injected,
                    matched_findings=case.audit.matched_findings,
                    expected_findings=case.audit.expected_findings,
                    source=case.source,
                )
            )
    finally:
        schema.load_priors = original_priors  # type: ignore[assignment]
        schema.load_rule_priors = original_rule_priors  # type: ignore[assignment]
        pipeline.load_priors = original_priors  # type: ignore[assignment]
        pipeline.load_rule_priors = original_rule_priors  # type: ignore[assignment]
        rule_posteriors.load_rule_priors = original_rule_priors  # type: ignore[assignment]
        load_priors.cache_clear()
        load_rule_priors.cache_clear()

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
        complexity_values = _neighbor_values(
            base.complexity_base, [1.8, 2.0, 2.05, 2.1, 2.2, 2.4]
        )
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
    """Prefer a tight band around the current center, falling back to the full grid."""
    band = [value for value in grid if abs(value - center) <= 0.35 or abs(value - center) <= 2.5]
    return sorted(set(band or grid))


def apply_config_to_priors(config: TuneConfig, *, rule_multiplier: float = 1.0) -> None:
    del rule_multiplier
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
    load_priors.cache_clear()
    load_rule_priors.cache_clear()


def compute_rule_prior_adjustments(
    cases: list[AuditCalibrationCase],
    rows: list[ComparisonRow],
    *,
    damping: float = 0.65,
) -> dict[str, float]:
    """Return rule_id -> multiplicative prior adjustment from audit/estimator ratios."""
    buckets: dict[str, list[float]] = {}
    for case, row in zip(cases, rows):
        if len(case.injected_rules) != 1:
            continue
        rule_id = case.injected_rules[0]
        audit = row.audit_target_usd
        estimate = row.estimator_central_usd
        if audit <= 0 or estimate <= 0:
            continue
        ratio = audit / estimate
        damped = ratio**damping if ratio < 1 else ratio**damping
        buckets.setdefault(rule_id, []).append(damped)

    adjustments: dict[str, float] = {}
    for rule_id, values in buckets.items():
        values = sorted(values)
        median = values[len(values) // 2]
        adjustments[rule_id] = min(max(median, 0.05), 8.0)
    return adjustments


def apply_rule_prior_adjustments(adjustments: dict[str, float]) -> int:
    if not adjustments:
        return 0
    text = RULE_PRIORS_PATH.read_text(encoding="utf-8")
    updated = 0
    for rule_id, multiplier in adjustments.items():
        pattern = rf"({re.escape(rule_id)}:\n\s+prior:\s+)([0-9.]+)"

        def _replace(match: re.Match[str], mult: float = multiplier) -> str:
            old = float(match.group(2))
            new = min(max(old * mult, 0.001), 0.5)
            return f"{match.group(1)}{new:.6f}".rstrip("0").rstrip(".")

        new_text, count = re.subn(pattern, _replace, text, count=1)
        if count:
            text = new_text
            updated += 1
    if updated:
        RULE_PRIORS_PATH.write_text(text, encoding="utf-8")
        load_rule_priors.cache_clear()
    return updated

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