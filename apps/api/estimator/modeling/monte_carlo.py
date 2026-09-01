import numpy as np

from estimator.modeling.hypotheses import HYPOTHESIS_IDS
from estimator.modeling.rule_posteriors import get_rule_ids


def complexity_leakage_scale(complexity_total: int, priors: dict) -> float:
    cfg = priors.get("monte_carlo", {}).get("complexity_scale", {})
    base = float(cfg.get("base", 1.0))
    exponent = float(cfg.get("exponent", 0.0))
    if base == 1.0 and exponent == 0.0:
        return 1.0
    return base * (max(complexity_total, 1) ** -exponent)


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
            overlap = rho * min(li, lj) * 0.30
            penalty += overlap
            pair_penalties[f"{hi}:{hj}"] = overlap

    adjusted = max(raw_total - penalty, 0.0)
    return adjusted, pair_penalties


def apply_family_overlap(
    rule_amounts: dict[str, float],
    rule_families: dict[str, str],
    family_rhos: dict[str, float],
) -> tuple[float, dict[str, float]]:
    raw_total = sum(rule_amounts.values())
    if raw_total <= 0:
        return 0.0, {}

    by_family: dict[str, list[tuple[str, float]]] = {}
    for rule_id, amount in rule_amounts.items():
        if amount <= 0:
            continue
        family = rule_families.get(rule_id, "operational")
        by_family.setdefault(family, []).append((rule_id, amount))

    penalty = 0.0
    pair_penalties: dict[str, float] = {}
    for family, items in by_family.items():
        rho = float(family_rhos.get(family, 0.45))
        items.sort(key=lambda x: x[1], reverse=True)
        for i, (rule_i, li) in enumerate(items):
            for rule_j, lj in items[i + 1 :]:
                overlap = rho * min(li, lj) * 0.30
                penalty += overlap
                pair_penalties[f"{rule_i}:{rule_j}"] = overlap

    return max(raw_total - penalty, 0.0), pair_penalties


def _draw_distribution(rng: np.random.Generator, cfg: dict) -> float:
    dist = cfg.get("distribution", "beta")
    if dist == "gamma":
        return float(rng.gamma(cfg.get("shape", 2), cfg.get("scale", 3)))
    return float(rng.beta(cfg.get("alpha", 2), cfg.get("beta", 6)))


def _smb_grandfathering_scale(arr: float, normalized: dict) -> float:
    """Lift estimates for small high-ACV companies with frequent grandfathering."""
    if arr >= 1_000_000:
        return 1.0
    customers = normalized.get("profile.customer_count")
    try:
        if customers is not None and float(customers) > 20:
            return 1.0
    except (TypeError, ValueError):
        pass
    grandfathering = str(normalized.get("contracts.grandfathering", ""))
    if grandfathering == "very_frequently":
        return 1.75
    if grandfathering == "frequently":
        return 1.25
    return 1.0


def _tail_multiplier(normalized: dict, rule_priors: dict) -> float:
    cfg = rule_priors.get("tail_fattening", {})
    conf_max = int(cfg.get("billing_confidence_max", 2))
    complexity_min = int(cfg.get("complexity_min", 8))
    billing_conf = normalized.get("confidence.billing_confidence")
    complexity = int(normalized.get("complexity.total", 0))
    grandfathering = str(normalized.get("contracts.grandfathering", ""))
    high_grandfathering = grandfathering in ("frequently", "very_frequently")
    severity_mult = float(cfg.get("severity_multiplier", 1.0))
    try:
        if billing_conf is not None and float(billing_conf) <= conf_max and complexity >= complexity_min:
            return severity_mult
    except (TypeError, ValueError):
        pass
    if high_grandfathering:
        return severity_mult
    return 1.0


def simulate_totals(
    rng: np.random.Generator,
    arr: float,
    segments: dict[str, float],
    rule_posteriors: dict[str, float],
    priors: dict,
    rule_priors: dict,
    simulation_count: int,
    complexity_total: int = 1,
    normalized: dict | None = None,
) -> tuple[
    np.ndarray,
    np.ndarray,
    np.ndarray,
    np.ndarray,
    dict[str, np.ndarray],
    dict[str, np.ndarray],
]:
    rules_cfg = rule_priors.get("rules", {})
    rule_ids = get_rule_ids(rule_priors)
    family_rhos = rule_priors.get("family_correlations", {})
    max_fraction = float(priors.get("max_leakage_fraction_of_arr", 0.35))
    mc_cfg = priors.get("monte_carlo", {})
    affected_cfg = mc_cfg.get("affected_rate", {"alpha": 2, "beta": 20})
    affected_alpha = int(affected_cfg.get("alpha", 2))
    affected_beta = int(affected_cfg.get("beta", 20))
    persistence_divisor = float(mc_cfg.get("persistence_divisor", 12))
    simulation_intensity = float(mc_cfg.get("simulation_intensity", 1.0))
    leakage_scale = complexity_leakage_scale(complexity_total, priors)
    tail_cfg = rule_priors.get("tail_fattening", {})
    persistence_tail = float(tail_cfg.get("persistence_multiplier", 1.0))
    tail_mult = _tail_multiplier(normalized or {}, rule_priors)
    smb_scale = _smb_grandfathering_scale(arr, normalized or {})

    base_map = {
        "arr": segments["arr"],
        "contract_arr": segments["contract_arr"],
        "discount_arr": segments["discount_arr"],
        "usage_arr": segments["usage_arr"],
        "seat_arr": segments["seat_arr"],
        "addon_arr": segments["addon_arr"],
        "international_arr": segments["international_arr"],
        "credit_arr": segments.get("credit_arr", segments["arr"] * 0.05),
        "billing_execution_arr": segments.get("billing_execution_arr", segments["arr"] * 0.15),
        "invoice_arr": segments.get("invoice_arr", segments["arr"]),
    }
    arr_uncertainty = float((normalized or {}).get("arr_uncertainty", 0.05))

    totals = np.zeros(simulation_count)
    gross_totals = np.zeros(simulation_count)
    detectable = np.zeros(simulation_count)
    recoverable = np.zeros(simulation_count)
    per_rule: dict[str, np.ndarray] = {rid: np.zeros(simulation_count) for rid in rule_ids}
    per_recoverable: dict[str, np.ndarray] = {rid: np.zeros(simulation_count) for rid in rule_ids}

    rule_families = {rid: cfg.get("leak_family", "operational") for rid, cfg in rules_cfg.items()}

    for sim in range(simulation_count):
        exposure_jitter = 1.0 + rng.uniform(-arr_uncertainty, arr_uncertainty)
        rule_amounts: dict[str, float] = {}
        rule_gross_amounts: dict[str, float] = {}
        rule_detectable: dict[str, float] = {}
        rule_recoverable: dict[str, float] = {}

        for rule_id in rule_ids:
            cfg = rules_cfg.get(rule_id, {})
            posterior = rule_posteriors.get(rule_id, 0.03)
            exposure_base = float(base_map.get(cfg.get("exposure_base", "arr"), arr))
            if exposure_base <= 0 or posterior <= 0:
                continue
            exposure = exposure_base * exposure_jitter
            affected = rng.beta(affected_alpha, affected_beta)
            severity = _draw_distribution(rng, cfg.get("severity", {})) * tail_mult
            persistence = (
                _draw_distribution(rng, cfg.get("persistence", {})) / persistence_divisor
            ) * (persistence_tail if tail_mult > 1.0 else 1.0)
            recoverability = _draw_distribution(rng, cfg.get("recoverability", {}))
            detectability = float(cfg.get("detectability", 0.7))
            gross_leakage = (
                exposure
                * affected
                * severity
                * persistence
                * leakage_scale
                * posterior
                * simulation_intensity
                * smb_scale
            )
            leakage = gross_leakage * recoverability
            rule_gross_amounts[rule_id] = gross_leakage
            rule_amounts[rule_id] = leakage
            rule_detectable[rule_id] = leakage * detectability
            rule_recoverable[rule_id] = leakage
            per_rule[rule_id][sim] = leakage
            per_recoverable[rule_id][sim] = rule_recoverable[rule_id]

        adjusted, _ = apply_family_overlap(rule_amounts, rule_families, family_rhos)
        gross_adjusted, _ = apply_family_overlap(rule_gross_amounts, rule_families, family_rhos)
        capped = min(adjusted, arr * max_fraction)
        gross_capped = min(gross_adjusted, arr * max_fraction)
        totals[sim] = capped
        gross_totals[sim] = gross_capped

        if rule_amounts:
            raw_det = sum(rule_detectable.values())
            raw_rec = sum(rule_recoverable.values())
            scale = capped / max(sum(rule_amounts.values()), 1e-9)
            detectable[sim] = min(raw_det * scale, capped)
            recoverable[sim] = min(raw_rec * scale, capped)

    return totals, gross_totals, detectable, recoverable, per_rule, per_recoverable


def rollup_hypothesis_samples(
    per_rule: dict[str, np.ndarray],
    rules_cfg: dict[str, dict],
) -> dict[str, np.ndarray]:
    per_hypothesis: dict[str, np.ndarray] = {}
    sim_count = next(iter(per_rule.values())).shape[0] if per_rule else 0
    for hid in HYPOTHESIS_IDS:
        samples = np.zeros(sim_count)
        for rule_id, cfg in rules_cfg.items():
            if hid in cfg.get("hypothesis_ids", []):
                samples += per_rule.get(rule_id, np.zeros(sim_count))
        per_hypothesis[hid] = samples
    return per_hypothesis


def percentiles(values: np.ndarray) -> dict[str, float]:
    return {
        "p10": float(np.percentile(values, 10)),
        "p25": float(np.percentile(values, 25)),
        "p50": float(np.percentile(values, 50)),
        "p75": float(np.percentile(values, 75)),
        "p90": float(np.percentile(values, 90)),
    }


def theoretical_stack_p90(per_rule: dict[str, np.ndarray]) -> float:
    total = 0.0
    for samples in per_rule.values():
        if samples.size == 0 or float(np.max(samples)) <= 0:
            continue
        total += float(np.percentile(samples, 90))
    return total
