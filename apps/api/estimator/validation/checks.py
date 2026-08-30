from typing import Any


def check_sanity(answers: dict[str, Any]) -> list[dict[str, str]]:
    warnings: list[dict[str, str]] = []
    arr = answers.get("profile.arr_amount")
    customers = answers.get("profile.customer_count")
    if arr and customers and customers > 0:
        acv = float(arr) / float(customers)
        if acv > 5_000_000:
            warnings.append(
                {
                    "code": "high_acv",
                    "message": "Your inputs suggest an unusually high average contract value. Please confirm.",
                }
            )
        if acv < 500 and float(arr) > 1_000_000:
            warnings.append(
                {
                    "code": "low_acv",
                    "message": "Your customer count seems high relative to ARR. Please review.",
                }
            )
    return warnings


def check_contradictions(answers: dict[str, Any]) -> list[dict[str, str]]:
    conflicts: list[dict[str, str]] = []
    usage = answers.get("pricing.usage_based")
    models = answers.get("pricing.models") or []
    if usage is False and "usage" in models:
        conflicts.append(
            {
                "code": "usage_model_mismatch",
                "message": "You selected usage pricing but indicated usage-based billing is not used.",
            }
        )
    manual_freq = answers.get("operations.manual_override_frequency")
    if manual_freq == "never" and answers.get("changes.migration_method") == "manual":
        conflicts.append(
            {
                "code": "manual_operations_mismatch",
                "message": "You reported no manual billing changes but manual pricing migration.",
            }
        )
    return conflicts
