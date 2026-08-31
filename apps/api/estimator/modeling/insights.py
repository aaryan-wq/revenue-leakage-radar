from typing import Any

RULE_DISPLAY_NAMES: dict[str, str] = {
    "grandfathered_pricing": "Grandfathered pricing",
    "legacy_pricing": "Legacy pricing",
    "renewal_price_drift": "Renewal price drift",
    "missing_scheduled_increase": "Missing scheduled increase",
    "expired_discount": "Expired discount still applied",
    "permanent_promotional_discount": "Permanent promotional discount",
    "manual_price_override": "Manual price override",
    "price_catalog_mismatch": "Price catalog mismatch",
    "incorrect_addon_price": "Incorrect add-on price",
    "discount_wrong_product": "Discount on wrong product",
    "incorrect_seat_price": "Incorrect seat price",
    "contract_billing_price_divergence": "Contract vs billing price divergence",
    "billing_frequency_mismatch": "Billing frequency mismatch",
    "orphaned_records": "Orphaned billing records",
    "duplicate_subscription": "Duplicate subscription",
    "currency_mismatch": "Currency mismatch",
    "discount_stacking": "Discount stacking",
    "duplicate_discount": "Duplicate discount",
    "excessive_discount": "Excessive discount",
    "invoice_price_mismatch": "Invoice price mismatch",
    "active_subscription_not_billing": "Active subscription not billing",
    "cancelled_subscription_still_billing": "Cancelled subscription still billing",
    "missing_expected_invoice": "Missing expected invoice",
    "credit_leakage": "Credit leakage",
    "duplicate_credit": "Duplicate credit",
    "duplicate_customer": "Duplicate customer",
    "usage_billing_drift": "Usage billing drift",
}

CATEGORY_LABELS = {
    "pricing": "Pricing",
    "discounts": "Discounts",
    "billing": "Billing",
    "credits": "Credits",
    "data_quality": "Data Quality",
}

EXPOSURE_BASE_LABELS: dict[str, str] = {
    "arr": "full ARR",
    "contract_arr": "negotiated contract ARR",
    "discount_arr": "discounted revenue pool",
    "usage_arr": "usage-rated ARR",
    "seat_arr": "seat-based ARR",
    "addon_arr": "add-on ARR",
    "international_arr": "international ARR",
    "credit_arr": "credit/refund exposure pool",
    "billing_execution_arr": "billing execution ARR",
    "invoice_arr": "invoice QA exposure pool",
}

ANSWER_DRIVERS: dict[str, str] = {
    "contracts.grandfathering": "grandfathering frequency",
    "contracts.negotiated_arr_pct": "negotiated ARR share",
    "contracts.renewal_increases": "renewal increase process",
    "discounts.frequency": "discount usage",
    "discounts.auto_expiry_removal": "automatic discount removal",
    "discounts.expiry_confidence": "discount expiry confidence",
    "operations.manual_override_frequency": "manual billing overrides",
    "systems.billing_system_count": "billing system count",
    "quote_to_bill.commercial_truth": "commercial truth source",
    "quote_to_bill.quote_automation": "quote-to-bill automation",
    "changes.pricing_changes_24mo": "recent pricing changes",
    "migrations.migrated_36mo": "recent migration",
    "migrations.parallel_systems": "parallel billing systems",
    "international.multi_currency": "multi-currency billing",
    "product.billable_count": "billable product count",
    "product.addons": "add-on catalog",
    "pricing.models": "pricing models",
    "usage.reconciliation": "usage reconciliation",
    "seats.reconciliation": "seat reconciliation",
    "controls.monthly_reconciliation": "reconciliation cadence",
}

HYPOTHESIS_DRIVER_KEYS: dict[str, list[str]] = {
    "H1": ["contracts.grandfathering", "changes.pricing_changes_24mo"],
    "H2": ["contracts.renewal_increases", "changes.pricing_changes_24mo"],
    "H3": ["discounts.frequency", "discounts.auto_expiry_removal"],
    "H4": ["discounts.frequency", "discounts.expiry_confidence"],
    "H5": ["product.billable_count", "product.independent_catalogs"],
    "H6": ["changes.pricing_changes_24mo"],
    "H7": ["product.billable_count"],
    "H8": ["product.addons"],
    "H9": ["product.addons"],
    "H10": ["seats.reconciliation", "pricing.models"],
    "H11": ["usage.reconciliation", "pricing.models"],
    "H12": ["quote_to_bill.commercial_truth", "quote_to_bill.quote_automation"],
    "H13": ["contracts.negotiated_arr_pct", "quote_to_bill.quote_automation"],
    "H14": ["migrations.migrated_36mo", "migrations.parallel_systems"],
    "H15": ["international.multi_currency"],
    "H16": ["operations.manual_override_frequency", "operations.unticketed_adjustments"],
    "H17": ["changes.pricing_changes_24mo", "changes.migration_method"],
    "H18": ["contracts.negotiated_arr_pct", "profile.customer_count"],
}


def build_insights(
    *,
    normalized: dict[str, Any],
    segments: dict[str, float],
    complexity: dict[str, Any],
    top_hypotheses: list[dict[str, Any]],
    rule_breakdown: list[dict[str, Any]] | None = None,
    estimate: dict[str, float],
    detectable: dict[str, float],
    arr: float,
    priors: dict[str, Any],
    rule_priors: dict[str, Any] | None = None,
    sim_stats: dict[str, float],
    scenario: str,
    scenario_band: tuple[str, str],
    simulation_count: int,
) -> dict[str, Any]:
    profile_summary = _build_profile_summary(normalized, complexity, arr)
    mechanism_insights = _build_mechanism_insights(normalized, top_hypotheses, segments, priors)
    rule_insights = _build_rule_insights(rule_breakdown or [], segments, rule_priors or {})
    verification_preview = _build_verification_preview_all(rule_breakdown or [])
    coverage_bridge = _build_coverage_bridge(rule_breakdown or [])
    calculation_summary = _build_calculation_summary(
        estimate=estimate,
        detectable=detectable,
        arr=arr,
        top_hypotheses=top_hypotheses,
        sim_stats=sim_stats,
        scenario=scenario,
        scenario_band=scenario_band,
        simulation_count=simulation_count,
        calibration_stage=int(priors.get("calibration_stage", 0)),
        complexity_score=int(complexity.get("total", 0)),
    )
    return {
        "profile_summary": profile_summary,
        "mechanism_insights": mechanism_insights,
        "rule_insights": rule_insights,
        "verification_preview": verification_preview,
        "coverage_bridge": coverage_bridge,
        "calculation_summary": calculation_summary,
        "executive_summary": calculation_summary["explanation_bullets"][0]
        if calculation_summary["explanation_bullets"]
        else "",
    }


def _fmt_usd(value: float) -> str:
    if value >= 1_000_000:
        text = f"${value / 1_000_000:.1f}M"
        return text.replace(".0M", "M")
    if value >= 1_000:
        return f"${value / 1_000:.0f}k"
    return f"${value:,.0f}"


def _format_answer_value(key: str, value: Any) -> str:
    if value is None:
        return "unknown"
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return ", ".join(str(item).replace("_", " ") for item in value)
    return str(value).replace("_", " ")


def _build_profile_summary(
    normalized: dict[str, Any], complexity: dict[str, Any], arr: float
) -> dict[str, Any]:
    customer_count = normalized.get("profile.customer_count")
    flags: list[str] = []

    checks: list[tuple[Any, str]] = [
        (normalized.get("contracts.grandfathering") in {"frequently", "very_frequently"}, "Frequent grandfathering"),
        (normalized.get("discounts.frequency") in {"common", "nearly_all"}, "Heavy discount usage"),
        (
            normalized.get("operations.manual_override_frequency") in {"frequently", "very_frequently"},
            "Frequent manual billing overrides",
        ),
        (normalized.get("systems.billing_system_count") == "3_plus", "Multiple billing systems"),
        (normalized.get("quote_to_bill.commercial_truth") == "multiple", "Multiple sources of commercial truth"),
        (normalized.get("migrations.migrated_36mo"), "Recent billing migration"),
        (normalized.get("international.multi_currency"), "Multi-currency billing"),
        (normalized.get("controls.monthly_reconciliation") == "never", "No monthly reconciliation"),
        (
            normalized.get("discounts.auto_expiry_removal") in {"rarely", "never"},
            "Discounts not removed automatically when they expire",
        ),
        (normalized.get("changes.pricing_changes_24mo") == "6_plus", "Six or more pricing changes in 24 months"),
    ]
    for condition, label in checks:
        if condition:
            flags.append(label)

    return {
        "arr_usd": arr,
        "customer_count": customer_count,
        "complexity_label": complexity.get("label", "Moderate"),
        "complexity_score": complexity.get("total", 0),
        "risk_flags": flags[:5],
    }


def _exposure_pool(hid: str, segments: dict[str, float], priors: dict[str, Any]) -> tuple[str, float]:
    cfg = priors.get("hypotheses", {}).get(hid, {})
    base_key = cfg.get("exposure_base", "arr")
    label = EXPOSURE_BASE_LABELS.get(base_key, base_key.replace("_", " "))
    amount = float(segments.get(base_key, segments.get("arr", 0.0)))
    return label, amount


def _driver_clause(hid: str, normalized: dict[str, Any]) -> str:
    keys = HYPOTHESIS_DRIVER_KEYS.get(hid, [])
    parts: list[str] = []
    for key in keys[:2]:
        value = normalized.get(key)
        if value is None:
            continue
        label = ANSWER_DRIVERS.get(key, key.split(".")[-1].replace("_", " "))
        parts.append(f"{label} = {_format_answer_value(key, value)}")
    if not parts:
        return "billing profile inputs"
    return "; ".join(parts)


def _build_mechanism_insights(
    normalized: dict[str, Any],
    top_hypotheses: list[dict[str, Any]],
    segments: dict[str, float],
    priors: dict[str, Any],
) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []
    for item in top_hypotheses:
        hid = item["hypothesis_id"]
        pool_label, pool_amount = _exposure_pool(hid, segments, priors)
        driver = _driver_clause(hid, normalized)
        insight = (
            f"{item['likelihood']:.0f}% mechanism weight from your answers × "
            f"{_fmt_usd(pool_amount)} {pool_label} → "
            f"{_fmt_usd(item['expected'])} modeled ({item['pct_of_arr']:.2f}% ARR, "
            f"{item['share_of_total']:.0f}% of top mechanisms). "
            f"Input driver: {driver}."
        )
        insights.append({"hypothesis_id": hid, "insight": insight})
    return insights


def _build_verification_preview(top_hypotheses: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preview: list[dict[str, Any]] = []
    seen_rules: set[str] = set()
    for item in top_hypotheses:
        rule_ids = item.get("rule_ids") or []
        rules = []
        for rule_id in rule_ids:
            if rule_id in seen_rules:
                continue
            seen_rules.add(rule_id)
            rules.append(
                {"rule_id": rule_id, "name": RULE_DISPLAY_NAMES.get(rule_id, rule_id.replace("_", " ").title())}
            )
        if rules:
            preview.append(
                {
                    "hypothesis_id": item["hypothesis_id"],
                    "hypothesis_name": item["name"],
                    "rules": rules,
                }
            )
    return preview


def _build_verification_preview_all(rule_breakdown: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_category: dict[str, list[dict[str, Any]]] = {}
    for row in rule_breakdown:
        category = row.get("category", "unknown")
        by_category.setdefault(category, []).append(
            {
                "rule_id": row["rule_id"],
                "name": RULE_DISPLAY_NAMES.get(row["rule_id"], row["rule_id"].replace("_", " ").title()),
                "expected": row.get("expected", 0),
                "posterior_probability": row.get("posterior_probability", 0),
                "detectability": row.get("detectability", 0),
                "required_entities": row.get("required_entities", []),
                "hypothesis_ids": row.get("hypothesis_ids", []),
            }
        )
    preview: list[dict[str, Any]] = []
    for category in sorted(by_category.keys()):
        preview.append(
            {
                "category": category,
                "category_label": CATEGORY_LABELS.get(category, category.replace("_", " ").title()),
                "rules": sorted(by_category[category], key=lambda r: r["expected"], reverse=True),
            }
        )
    return preview


def _build_rule_insights(
    rule_breakdown: list[dict[str, Any]],
    segments: dict[str, float],
    rule_priors: dict[str, Any],
) -> list[dict[str, str]]:
    rules_cfg = rule_priors.get("rules", {})
    insights: list[dict[str, str]] = []
    for row in rule_breakdown[:8]:
        rule_id = row["rule_id"]
        cfg = rules_cfg.get(rule_id, {})
        base_key = cfg.get("exposure_base", "arr")
        pool_label = EXPOSURE_BASE_LABELS.get(base_key, base_key)
        pool_amount = float(segments.get(base_key, segments.get("arr", 0.0)))
        name = RULE_DISPLAY_NAMES.get(rule_id, rule_id.replace("_", " ").title())
        insight = (
            f"{row['likelihood']:.0f}% rule weight × {_fmt_usd(pool_amount)} {pool_label} → "
            f"{_fmt_usd(row['expected'])} modeled for {name}."
        )
        insights.append({"rule_id": rule_id, "insight": insight})
    return insights


def _build_coverage_bridge(rule_breakdown: list[dict[str, Any]]) -> dict[str, Any]:
    entity_labels = {
        "customer": "Customers",
        "subscription": "Subscriptions",
        "invoice": "Invoices",
        "invoice_line_item": "Invoice Line Items",
        "coupon": "Coupons",
        "price": "Prices",
        "contract": "Contracts",
        "account": "CRM Accounts",
    }
    high_priority = [row for row in rule_breakdown if row.get("expected", 0) > 0][:12]
    entity_counts: dict[str, int] = {}
    for row in high_priority:
        for entity in row.get("required_entities", []):
            entity_counts[entity] = entity_counts.get(entity, 0) + 1
    file_suggestions = [
        f"Upload {entity_labels.get(entity, entity)}.csv to unlock {count} high-priority rules"
        for entity, count in sorted(entity_counts.items(), key=lambda item: item[1], reverse=True)[:4]
    ]
    return {
        "high_priority_rules": [row["rule_id"] for row in high_priority],
        "file_suggestions": file_suggestions,
        "total_rules_modeled": len(rule_breakdown),
    }


def _band_label(scenario_band: tuple[str, str], high_key: str) -> str:
    low_key, default_high = scenario_band
    high_label = high_key.upper().replace("P", "P")
    return f"{low_key.upper()} to {high_label}"


def _build_calculation_summary(
    *,
    estimate: dict[str, float],
    detectable: dict[str, float],
    arr: float,
    top_hypotheses: list[dict[str, Any]],
    sim_stats: dict[str, float],
    scenario: str,
    scenario_band: tuple[str, str],
    simulation_count: int,
    calibration_stage: int,
    complexity_score: int,
) -> dict[str, Any]:
    expected = estimate["central"]
    median_run = sim_stats["median_run"]
    pct_runs = sim_stats["pct_runs_with_leakage"]
    conditional_mean = sim_stats["conditional_mean"]
    pct_of_arr = round((expected / arr) * 100, 2) if arr > 0 else 0.0
    band_label = _band_label(scenario_band, sim_stats.get("high_band_key", scenario_band[1]))

    bullets: list[str] = []
    if expected <= 0:
        bullets.append(
            f"No positive recoverable revenue was estimated for {_fmt_usd(arr)} ARR based on your answers. "
            "A billing scan on actual records may surface leakage."
        )
    else:
        bullets.append(
            f"Based on {_fmt_usd(arr)} ARR and your questionnaire answers, "
            f"estimated recoverable revenue is up to {_fmt_usd(estimate['high'])} per year."
        )
        high_pct = round((estimate["high"] / arr) * 100, 1) if arr > 0 else 0.0
        bullets.append(
            f"That is about {high_pct:.1f}% of ARR. "
            "This is directional guidance, not an audited finding."
        )
        if top_hypotheses:
            top_line = ", ".join(
                f"{item['name']} (~{_fmt_usd(item['high'])})"
                for item in top_hypotheses[:3]
            )
            bullets.append(f"Largest likely sources: {top_line}. Categories overlap and are not additive.")
        det_high = detectable.get("high", 0)
        if det_high > 0:
            bullets.append(
                f"Up to {_fmt_usd(det_high)} may be confirmable from standard billing exports."
            )
        if calibration_stage >= 1:
            bullets.append(
                "A free billing scan can replace this estimate with evidence-backed findings."
            )

    return {
        "simulation_count": simulation_count,
        "expected_value": expected,
        "median_run": median_run,
        "pct_runs_with_leakage": pct_runs,
        "conditional_mean": conditional_mean,
        "gross_expected": estimate.get("gross_expected"),
        "net_recoverable": estimate.get("net_recoverable", expected),
        "pct_of_arr": pct_of_arr,
        "scenario": scenario,
        "scenario_band_label": band_label,
        "range_low": estimate["low"],
        "range_high": estimate["high"],
        "explanation_bullets": bullets,
    }
