import logging
from decimal import Decimal
from typing import Any

from ai.prompts.summary import EXECUTIVE_SUMMARY_SYSTEM, EXECUTIVE_SUMMARY_USER_TEMPLATE
from ai.provider import AIProviderError, call_openai_json
from reports.findings import category_label

logger = logging.getLogger(__name__)


def _fallback_narrative(metrics: dict[str, Any]) -> str:
    recoverable = metrics.get("recoverable_arr", "0")
    finding_count = metrics.get("finding_count", 0)
    confidence = metrics.get("confidence")
    breakdown = metrics.get("opportunity_breakdown", [])

    top = breakdown[:3] if breakdown else []
    top_lines = ", ".join(f"{row['label']} (${row['arr']})" for row in top) if top else "multiple billing categories"

    conf_text = f"{confidence}% confidence" if confidence else "moderate confidence"
    return (
        f"This revenue verification identified ${recoverable} in estimated recoverable annual recurring revenue "
        f"across {finding_count} findings with {conf_text}. "
        f"The largest opportunities are concentrated in {top_lines}. "
        "Each finding is backed by deterministic verification rules comparing billing records against catalog "
        "and contract data. Prioritize remediation starting with the highest-ARR categories to maximize "
        "near-term revenue recovery."
    )


def generate_executive_narrative(metrics: dict[str, Any]) -> str:
    breakdown = metrics.get("opportunity_breakdown", [])
    breakdown_lines = "\n".join(
        f"- {row['label']}: ${row['arr']} ARR, {row['issue_count']} issues"
        for row in breakdown
    ) or "- No categorized opportunities"
    top_categories = ", ".join(category_label(row["category"]) for row in breakdown[:3]) or "N/A"

    user_prompt = EXECUTIVE_SUMMARY_USER_TEMPLATE.format(
        recoverable_arr=metrics.get("recoverable_arr", "0"),
        confidence=metrics.get("confidence") or "N/A",
        finding_count=metrics.get("finding_count", 0),
        accounts_reviewed=metrics.get("accounts_reviewed", 0),
        invoices_reviewed=metrics.get("invoices_reviewed", 0),
        breakdown_lines=breakdown_lines,
        top_categories=top_categories,
    )

    try:
        result = call_openai_json(EXECUTIVE_SUMMARY_SYSTEM, user_prompt)
        narrative = result.get("narrative", "").strip()
        if narrative:
            return narrative
    except AIProviderError:
        logger.info("AI executive summary unavailable; using template fallback")

    return _fallback_narrative(metrics)
