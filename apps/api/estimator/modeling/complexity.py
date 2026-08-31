from typing import Any


def compute_complexity(normalized: dict[str, Any]) -> dict[str, int]:
    pricing = _pricing_score(normalized)
    contract = _contract_score(normalized)
    systems = _systems_score(normalized)
    change = _change_score(normalized)
    operations = _operations_score(normalized)
    total = pricing + contract + systems + change + operations
    return {
        "pricing": pricing,
        "contract": contract,
        "systems": systems,
        "change": change,
        "operations": operations,
        "total": total,
        "label": _complexity_label(total),
    }


def _complexity_label(total: int) -> str:
    if total <= 12:
        return "Low"
    if total <= 22:
        return "Moderate"
    if total <= 32:
        return "High"
    return "Very High"


def _pricing_score(n: dict[str, Any]) -> int:
    score = 0
    models = n.get("pricing.models") or []
    score += min(len(models), 4)
    if n.get("pricing.usage_based"):
        score += 2
    if n.get("pricing.seat_based"):
        score += 1
    product_count = n.get("product.billable_count", "1")
    score += {"1": 0, "2": 1, "3_5": 2, "6_10": 3, "11_25": 4, "25_plus": 5}.get(product_count, 1)
    return min(score, 8)


def _contract_score(n: dict[str, Any]) -> int:
    score = 0
    negotiated = n.get("contracts.negotiated_arr_pct", "0")
    score += {"0": 0, "1_25": 1, "26_50": 2, "51_75": 4, "76_100": 6}.get(negotiated, 1)
    grandfather = n.get("contracts.grandfathering", "never")
    score += {"never": 0, "rarely": 1, "sometimes": 2, "frequently": 4, "very_frequently": 6, "unknown": 2}.get(
        grandfather, 1
    )
    return min(score, 8)


def _systems_score(n: dict[str, Any]) -> int:
    count = n.get("systems.billing_system_count", "1")
    score = {"1": 0, "2": 3, "3_plus": 6, "unknown": 2}.get(count, 1)
    truth = n.get("quote_to_bill.commercial_truth", "billing")
    if truth in {"multiple", "undefined", "spreadsheet"}:
        score += 2
    return min(score, 8)


def _change_score(n: dict[str, Any]) -> int:
    changes = n.get("changes.pricing_changes_24mo", "0")
    score = {"0": 0, "1": 1, "2_3": 3, "4_5": 5, "6_plus": 7}.get(changes, 1)
    if n.get("migrations.migrated_36mo"):
        score += 2
    return min(score, 8)


def _operations_score(n: dict[str, Any]) -> int:
    manual = n.get("operations.manual_override_frequency", "never")
    score = {"never": 0, "rarely": 1, "sometimes": 3, "frequently": 5, "very_frequently": 7, "unknown": 2}.get(
        manual, 1
    )
    recon = n.get("controls.monthly_reconciliation", "unknown")
    if recon in {"never", "occasionally", "unknown"}:
        score += 2
    if not n.get("controls.billing_owner"):
        score += 1
    return min(score, 8)
