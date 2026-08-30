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
}

GRANDFATHERING_LABELS = {
    "never": "no grandfathering",
    "rarely": "rare grandfathering",
    "sometimes": "occasional grandfathering",
    "frequently": "frequent grandfathering",
    "very_frequently": "very frequent grandfathering",
}

DISCOUNT_FREQ_LABELS = {
    "never": "minimal discount usage",
    "rare": "rare discounts",
    "occasional": "occasional discounts",
    "common": "common discounts",
    "nearly_all": "discounts on nearly all deals",
}

MANUAL_OVERRIDE_LABELS = {
    "never": "no manual overrides",
    "rarely": "rare manual overrides",
    "sometimes": "occasional manual overrides",
    "frequently": "frequent manual overrides",
    "very_frequently": "very frequent manual overrides",
}


def build_insights(
    *,
    normalized: dict[str, Any],
    segments: dict[str, float],
    complexity: dict[str, Any],
    top_hypotheses: list[dict[str, Any]],
    estimate: dict[str, float],
    detectable: dict[str, float],
    arr: float,
) -> dict[str, Any]:
    profile_summary = _build_profile_summary(normalized, complexity, arr)
    mechanism_insights = _build_mechanism_insights(normalized, top_hypotheses)
    verification_preview = _build_verification_preview(top_hypotheses)
    executive_summary = _build_executive_summary(
        normalized, estimate, detectable, top_hypotheses, profile_summary
    )
    return {
        "profile_summary": profile_summary,
        "mechanism_insights": mechanism_insights,
        "verification_preview": verification_preview,
        "executive_summary": executive_summary,
    }


def _build_profile_summary(
    normalized: dict[str, Any], complexity: dict[str, Any], arr: float
) -> dict[str, Any]:
    customer_count = normalized.get("profile.customer_count")
    flags: list[str] = []

    grandfather = normalized.get("contracts.grandfathering", "never")
    if grandfather in {"frequently", "very_frequently"}:
        flags.append("Frequent grandfathering")

    discount_freq = normalized.get("discounts.frequency", "never")
    if discount_freq in {"common", "nearly_all"}:
        flags.append("Heavy discount usage")

    manual = normalized.get("operations.manual_override_frequency", "never")
    if manual in {"frequently", "very_frequently"}:
        flags.append("Frequent manual billing overrides")

    if normalized.get("systems.billing_system_count") == "3_plus":
        flags.append("Multiple billing systems")

    if normalized.get("quote_to_bill.commercial_truth") == "multiple":
        flags.append("Multiple sources of commercial truth")

    if normalized.get("migrations.migrated_36mo"):
        flags.append("Recent billing migration")

    if normalized.get("international.multi_currency"):
        flags.append("Multi-currency billing")

    if normalized.get("controls.monthly_reconciliation") == "never":
        flags.append("No monthly reconciliation")

    expiry = normalized.get("discounts.expiry_handling")
    if expiry in {"manual_sales", "manual_revops", "manual_finance"}:
        flags.append("Manual discount expiry handling")

    if normalized.get("changes.pricing_changes_24mo") == "6_plus":
        flags.append("Six or more pricing changes in 24 months")

    return {
        "arr_usd": arr,
        "customer_count": customer_count,
        "complexity_label": complexity.get("label", "Moderate"),
        "complexity_score": complexity.get("total", 0),
        "risk_flags": flags[:5],
    }


def _build_mechanism_insights(
    normalized: dict[str, Any], top_hypotheses: list[dict[str, Any]]
) -> list[dict[str, str]]:
    insights: list[dict[str, str]] = []
    for item in top_hypotheses:
        hid = item["hypothesis_id"]
        sentence = _mechanism_sentence(hid, normalized, item["name"])
        insights.append({"hypothesis_id": hid, "insight": sentence})
    return insights


def _mechanism_sentence(hid: str, n: dict[str, Any], name: str) -> str:
    builders = {
        "H1": _insight_h1,
        "H2": _insight_h2,
        "H3": _insight_h3,
        "H4": _insight_h4,
        "H5": _insight_h5,
        "H6": _insight_h6,
        "H7": _insight_h7,
        "H8": _insight_h8,
        "H9": _insight_h9,
        "H10": _insight_h10,
        "H11": _insight_h11,
        "H12": _insight_h12,
        "H13": _insight_h13,
        "H14": _insight_h14,
        "H15": _insight_h15,
        "H16": _insight_h16,
        "H17": _insight_h17,
        "H18": _insight_h18,
    }
    builder = builders.get(hid)
    if builder:
        return builder(n, name)
    return f"Your billing profile increases plausibility of {name.lower()}."


def _insight_h1(n: dict[str, Any], name: str) -> str:
    gf = GRANDFATHERING_LABELS.get(n.get("contracts.grandfathering", "never"), "grandfathering")
    return f"You reported {gf}, which often leaves legacy rates on active subscriptions ({name.lower()})."


def _insight_h2(n: dict[str, Any], name: str) -> str:
    renewal = n.get("contracts.renewal_increases", "yes")
    if renewal == "manual":
        return f"Manual renewal increases increase the chance that list prices drift from billed rates ({name.lower()})."
    changes = n.get("changes.pricing_changes_24mo", "0")
    if changes in {"4_5", "6_plus"}:
        return f"Frequent pricing changes ({changes.replace('_', ' to ')}) make renewal drift harder to track ({name.lower()})."
    return f"Contract and pricing change patterns suggest renewal drift risk ({name.lower()})."


def _insight_h3(n: dict[str, Any], name: str) -> str:
    freq = DISCOUNT_FREQ_LABELS.get(n.get("discounts.frequency", "never"), "discount usage")
    expiry = n.get("discounts.expiry_handling", "unknown")
    if expiry != "automatic":
        return f"With {freq} and non-automatic discount expiry, expired promotions may keep billing ({name.lower()})."
    return f"Given {freq}, expired discounts may persist on invoices ({name.lower()})."


def _insight_h4(n: dict[str, Any], name: str) -> str:
    freq = DISCOUNT_FREQ_LABELS.get(n.get("discounts.frequency", "never"), "discount usage")
    conf = n.get("discounts.expiry_confidence")
    conf_note = f" (confidence {conf}/5)" if conf is not None else ""
    return f"{freq.capitalize()}{conf_note} raises the odds that manual discounts stay on accounts ({name.lower()})."


def _insight_h5(n: dict[str, Any], name: str) -> str:
    products = n.get("product.billable_count", "1")
    catalogs = n.get("product.independent_catalogs", "no")
    if catalogs == "yes":
        return f"Multiple billable products ({products.replace('_', ' to ')}) with independent catalogs increase catalog drift risk ({name.lower()})."
    return f"A broad product catalog ({products.replace('_', ' to ')}) increases catalog drift risk ({name.lower()})."


def _insight_h6(n: dict[str, Any], name: str) -> str:
    changes = n.get("changes.pricing_changes_24mo", "0")
    return f"{changes.replace('_', ' to ')} pricing changes in 24 months suggest active price versions may not match billed rates ({name.lower()})."


def _insight_h7(n: dict[str, Any], name: str) -> str:
    products = n.get("product.billable_count", "1")
    return f"With {products.replace('_', ' to ')} billable products, SKU mapping errors can misprice line items ({name.lower()})."


def _insight_h8(n: dict[str, Any], name: str) -> str:
    if n.get("product.addons"):
        return "Add-ons and bundles in your catalog increase bundle composition drift risk (bundle drift)."
    return "Product bundle configuration increases bundle drift risk (bundle drift)."


def _insight_h9(n: dict[str, Any], name: str) -> str:
    if n.get("product.addons"):
        return "Add-on products in your stack often drift from catalog pricing over time (add-on drift)."
    return "Add-on pricing can drift when catalog updates outpace subscription records (add-on drift)."


def _insight_h10(n: dict[str, Any], name: str) -> str:
    recon = n.get("seats.reconciliation", "unknown")
    if recon == "manual":
        return "Manual seat reconciliation makes seat count mismatches more likely (seat pricing drift)."
    return "Per-seat pricing with imperfect reconciliation increases seat pricing drift risk."


def _insight_h11(n: dict[str, Any], name: str) -> str:
    usage_recon = n.get("usage.reconciliation", "unknown")
    rating = n.get("usage.rating", "unknown")
    return f"Usage-based billing ({rating.replace('_', ' ')}, {usage_recon} reconciliation) increases usage billing drift risk."


def _insight_h12(n: dict[str, Any], name: str) -> str:
    truth = n.get("quote_to_bill.commercial_truth", "billing")
    automation = n.get("quote_to_bill.quote_automation", "unknown")
    if truth == "multiple":
        return f"Multiple commercial truth sources and {automation.replace('_', ' ')} quote-to-bill flow increase quote vs billing gaps."
    return f"Quote-to-bill automation ({automation.replace('_', ' ')}) affects how often quoted terms match invoices."


def _insight_h13(n: dict[str, Any], name: str) -> str:
    negotiated = n.get("contracts.negotiated_arr_pct", "0")
    custom = n.get("contracts.custom_pricing", "no")
    return f"Custom enterprise terms ({negotiated.replace('_', ' to ')}% negotiated ARR, custom pricing {custom}) increase contract configuration drift."


def _insight_h14(n: dict[str, Any], name: str) -> str:
    if n.get("migrations.parallel_systems"):
        return "Parallel billing systems after migration increase orphaned or duplicate record risk (migration errors)."
    return "A recent billing migration increases the chance of cutover errors (migration errors)."


def _insight_h15(n: dict[str, Any], name: str) -> str:
    count = n.get("international.currency_count", "unknown")
    return f"Multi-currency billing ({count.replace('_', ' to ')} currencies) increases FX and currency configuration drift."


def _insight_h16(n: dict[str, Any], name: str) -> str:
    manual = MANUAL_OVERRIDE_LABELS.get(
        n.get("operations.manual_override_frequency", "never"), "manual overrides"
    )
    logging = n.get("operations.manual_change_logging", "unknown")
    log_note = " without consistent logging" if logging == "no" else ""
    return f"You reported {manual}{log_note}, which raises manual override persistence risk."


def _insight_h17(n: dict[str, Any], name: str) -> str:
    velocity = n.get("velocity.commercial_changes_12mo", "0")
    return f"{velocity.replace('_', ' to ')} commercial changes in 12 months suggest catalog updates may outpace billing records (product launch drift)."


def _insight_h18(n: dict[str, Any], name: str) -> str:
    customers = n.get("profile.customer_count", 0)
    negotiated = n.get("contracts.negotiated_arr_pct", "0")
    return f"Enterprise scale ({customers} customers, {negotiated.replace('_', ' to ')}% negotiated ARR) compounds contract, seat, and discount leakage mechanisms."


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
            rules.append({"rule_id": rule_id, "name": RULE_DISPLAY_NAMES.get(rule_id, rule_id.replace("_", " ").title())})
        if rules:
            preview.append(
                {
                    "hypothesis_id": item["hypothesis_id"],
                    "hypothesis_name": item["name"],
                    "rules": rules,
                }
            )
    return preview


def _build_executive_summary(
    normalized: dict[str, Any],
    estimate: dict[str, float],
    detectable: dict[str, float],
    top_hypotheses: list[dict[str, Any]],
    profile_summary: dict[str, Any],
) -> str:
    low = estimate["low"]
    high = estimate["high"]
    central = estimate["central"]
    arr = profile_summary["arr_usd"]
    complexity = profile_summary["complexity_label"]
    customers = profile_summary.get("customer_count")

    if central <= 0:
        return (
            "Based on your inputs, the model did not identify meaningful recurring-revenue exposure. "
            "A deterministic billing scan can still confirm whether hidden leakage exists."
        )

    parts = [
        f"For roughly ${arr:,.0f} ARR",
    ]
    if customers:
        parts[0] += f" across about {customers:,} customers"
    parts[0] += f", the model estimates ${low:,.0f} to ${high:,.0f} in recoverable recurring revenue (expected ${central:,.0f})."

    if top_hypotheses:
        top_names = ", ".join(h["name"].lower() for h in top_hypotheses[:3])
        parts.append(f"Top mechanisms: {top_names}.")

    if profile_summary.get("risk_flags"):
        flags = ", ".join(f.lower() for f in profile_summary["risk_flags"][:3])
        parts.append(f"Your profile flags {flags} ({complexity.lower()} billing complexity).")

    det_low = detectable.get("low", 0)
    det_high = detectable.get("high", 0)
    if det_high > 0:
        parts.append(
            f"Of this range, roughly ${det_low:,.0f} to ${det_high:,.0f} is likely identifiable from standard billing exports."
        )

    return " ".join(parts)
