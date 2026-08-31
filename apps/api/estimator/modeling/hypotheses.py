from typing import Any

HYPOTHESIS_IDS = [f"H{i}" for i in range(1, 19)]


def compute_posteriors(normalized: dict[str, Any], priors: dict[str, Any]) -> dict[str, float]:
    result: dict[str, float] = {}
    hypothesis_cfg = priors.get("hypotheses", {})
    for hid in HYPOTHESIS_IDS:
        cfg = hypothesis_cfg.get(hid, {})
        prior = float(cfg.get("prior", 0.05))
        odds = prior / max(1 - prior, 1e-6)
        odds *= _likelihood_ratio(hid, normalized)
        posterior = odds / (1 + odds)
        result[hid] = min(max(posterior, 0.001), 0.95)
    return result


def _likelihood_ratio(hid: str, n: dict[str, Any]) -> float:
    lr = 1.0
    if hid in {"H1", "H2", "H6"}:
        grandfather = n.get("contracts.grandfathering", "never")
        lr *= {"never": 0.5, "rarely": 0.8, "sometimes": 1.2, "frequently": 1.8, "very_frequently": 2.5, "unknown": 1.3}.get(
            grandfather, 1.0
        )
        changes = n.get("changes.pricing_changes_24mo", "0")
        lr *= {"0": 0.6, "1": 1.0, "2_3": 1.4, "4_5": 1.8, "6_plus": 2.2}.get(changes, 1.0)
    if hid in {"H3", "H4"}:
        freq = n.get("discounts.frequency", "never")
        lr *= {"never": 0.3, "rare": 0.7, "occasional": 1.2, "common": 1.8, "nearly_all": 2.5}.get(freq, 1.0)
        auto_expiry = n.get("discounts.auto_expiry_removal", "unknown")
        lr *= {"always": 0.5, "usually": 0.7, "sometimes": 1.2, "rarely": 1.6, "never": 2.0, "unknown": 1.4}.get(
            auto_expiry, 1.0
        )
        conf = n.get("discounts.expiry_confidence")
        if conf is not None:
            lr *= 1.0 + (5 - float(conf)) * 0.15
    if hid in {"H5", "H7", "H8", "H9"}:
        products = n.get("product.billable_count", "1")
        lr *= {"1": 0.5, "2": 0.8, "3_5": 1.1, "6_10": 1.5, "11_25": 2.0, "25_plus": 2.5}.get(products, 1.0)
    if hid == "H10":
        if n.get("pricing.seat_based"):
            lr *= 1.8
        recon = n.get("seats.reconciliation", "unknown")
        lr *= {"automatic": 0.6, "manual": 1.8, "unknown": 1.4}.get(recon, 1.0)
    if hid == "H11":
        if n.get("pricing.usage_based"):
            lr *= 2.0
        usage_recon = n.get("usage.reconciliation", "unknown")
        lr *= {"automated": 0.5, "partial": 1.0, "manual": 1.8, "unknown": 1.4}.get(usage_recon, 1.0)
    if hid in {"H12", "H13", "H18"}:
        negotiated = n.get("contracts.negotiated_arr_pct", "0")
        lr *= {"0": 0.4, "1_25": 0.8, "26_50": 1.2, "51_75": 1.7, "76_100": 2.2}.get(negotiated, 1.0)
        automation = n.get("quote_to_bill.quote_automation", "unknown")
        lr *= {"fully": 0.5, "mostly": 0.7, "partial": 1.2, "mostly_manual": 1.8, "manual": 2.2, "unknown": 1.4}.get(
            automation, 1.0
        )
    if hid == "H14":
        if n.get("migrations.migrated_36mo"):
            lr *= 2.0
        if n.get("migrations.parallel_systems"):
            lr *= 1.5
    if hid == "H15":
        if n.get("international.multi_currency"):
            lr *= 2.0
    if hid == "H16":
        manual = n.get("operations.manual_override_frequency", "never")
        lr *= {"never": 0.4, "rarely": 0.8, "sometimes": 1.4, "frequently": 2.0, "very_frequently": 2.8, "unknown": 1.3}.get(
            manual, 1.0
        )
    if hid == "H17":
        changes = n.get("changes.pricing_changes_24mo", "0")
        lr *= {"0": 0.5, "1": 0.8, "2_3": 1.2, "4_5": 1.7, "6_plus": 2.2}.get(changes, 1.0)
    billing_conf = n.get("confidence.billing_confidence")
    if billing_conf is not None:
        lr *= 1.0 + (5 - float(billing_conf)) * 0.08
    return max(lr, 0.1)
