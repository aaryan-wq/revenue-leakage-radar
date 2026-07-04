"""Primary/secondary attribution to prevent double-counting recoverable ARR."""

from __future__ import annotations

import hashlib
import uuid
from collections import defaultdict
from collections.abc import Callable
from decimal import Decimal

from verification.findings.generator import RULE_PRIORITY
from verification.recoverable import finding_recoverable_amount
from verification.types import LeakFamily, RuleFinding


def _scope_key(finding: RuleFinding) -> str:
    if finding.subscription_id:
        return f"sub:{finding.subscription_id}"
    if finding.customer_id:
        return f"cust:{finding.customer_id}"
    if finding.invoice_id:
        return f"inv:{finding.invoice_id}"
    if finding.product_id:
        return f"prod:{finding.product_id}"
    return f"finding:{finding.rule_id}"


def _monthly_bucket(finding: RuleFinding) -> Decimal:
    monthly = finding.estimated_monthly_loss or Decimal("0")
    return monthly.quantize(Decimal("0.01"))


def _stable_finding_key(finding: RuleFinding) -> str:
    parts = [
        finding.rule_id,
        finding.customer_id or "",
        finding.subscription_id or "",
        finding.invoice_id or "",
        finding.product_id or "",
        str(finding.expected_value or ""),
        str(finding.actual_value or ""),
    ]
    return "|".join(parts)


def _rank_finding(finding: RuleFinding) -> tuple[Decimal, Decimal, int]:
    priority = RULE_PRIORITY.get(finding.rule_id, 0)
    return (finding_recoverable_amount(finding), finding.confidence, priority)


def _rank_overlap_winner(finding: RuleFinding) -> tuple[Decimal, Decimal, int]:
    priority = RULE_PRIORITY.get(finding.rule_id, 0)
    return (finding_recoverable_amount(finding), finding.confidence, priority)


def _invoice_monthly_key(finding: RuleFinding) -> str | None:
    if finding_recoverable_amount(finding) <= 0 or not finding.invoice_id:
        return None
    return f"inv:{finding.invoice_id}:{_monthly_bucket(finding)}"


def _subscription_product_monthly_key(finding: RuleFinding) -> str | None:
    if finding_recoverable_amount(finding) <= 0 or not finding.subscription_id:
        return None
    product = finding.product_id or "*"
    return f"sub:{finding.subscription_id}:{product}:{_monthly_bucket(finding)}"


def _deterministic_group_ref(audit_id: uuid.UUID | str, scope_key: str, family: LeakFamily) -> str:
    raw = f"{audit_id}:{scope_key}:{family}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _secondary_ref(
    audit_id: uuid.UUID | str | None,
    finding: RuleFinding,
    scope_key: str,
    *,
    suffix: str,
) -> str | None:
    if finding.finding_ref:
        return finding.finding_ref
    if audit_id is None:
        return None
    trace_hash = (
        finding.calculation_trace.trace_hash_input()
        if finding.calculation_trace
        else hashlib.sha256(_stable_finding_key(finding).encode()).hexdigest()[:16]
    )
    raw = f"{audit_id}:{finding.rule_id}:{scope_key}:{trace_hash}:{suffix}"
    return hashlib.sha256(raw.encode()).hexdigest()[:16]


def _attribute_within_family(
    findings: list[RuleFinding],
    *,
    audit_id: uuid.UUID | str | None,
) -> list[RuleFinding]:
    groups: dict[tuple[str, LeakFamily], list[RuleFinding]] = {}
    for finding in findings:
        family = finding.leak_family or "operational"
        key = (_scope_key(finding), family)
        groups.setdefault(key, []).append(finding)

    attributed: list[RuleFinding] = []
    for (scope_key, family), group in groups.items():
        ranked = sorted(group, key=_rank_finding, reverse=True)
        primary = ranked[0]
        primary_ref = primary.finding_ref
        if not primary_ref and audit_id is not None:
            primary_ref = _deterministic_group_ref(audit_id, scope_key, family)
        attributed.append(
            primary.model_copy(
                update={
                    "attribution": "primary",
                    "primary_finding_ref": None,
                    "finding_ref": primary_ref,
                }
            )
        )
        for secondary in ranked[1:]:
            secondary_ref = _secondary_ref(audit_id, secondary, scope_key, suffix="secondary")
            attributed.append(
                secondary.model_copy(
                    update={
                        "attribution": "secondary",
                        "primary_finding_ref": primary_ref,
                        "finding_ref": secondary_ref,
                    }
                )
            )
    return attributed


def _dedupe_primaries_by_key(
    findings: list[RuleFinding],
    key_fn: Callable[[RuleFinding], str | None],
    *,
    audit_id: uuid.UUID | str | None,
    suffix: str,
) -> list[RuleFinding]:
    primaries = [finding for finding in findings if finding.attribution == "primary"]
    secondaries = [finding for finding in findings if finding.attribution != "primary"]

    overlap_groups: dict[str, list[RuleFinding]] = defaultdict(list)
    for finding in primaries:
        overlap_key = key_fn(finding)
        if overlap_key is None:
            overlap_groups[f"solo:{finding.finding_ref or _stable_finding_key(finding)}"].append(finding)
        else:
            overlap_groups[overlap_key].append(finding)

    deduped_primaries: list[RuleFinding] = []
    demoted: list[RuleFinding] = []
    for group in overlap_groups.values():
        if len(group) == 1:
            deduped_primaries.append(group[0])
            continue
        ranked = sorted(group, key=_rank_overlap_winner, reverse=True)
        winner = ranked[0]
        winner_ref = winner.finding_ref
        if not winner_ref and audit_id is not None:
            winner_ref = _deterministic_group_ref(
                audit_id,
                _scope_key(winner),
                winner.leak_family or "operational",
            )
            winner = winner.model_copy(update={"finding_ref": winner_ref})
        deduped_primaries.append(
            winner.model_copy(
                update={
                    "attribution": "primary",
                    "primary_finding_ref": None,
                }
            )
        )
        for loser in ranked[1:]:
            loser_ref = _secondary_ref(audit_id, loser, _scope_key(loser), suffix=suffix)
            demoted.append(
                loser.model_copy(
                    update={
                        "attribution": "secondary",
                        "primary_finding_ref": winner_ref,
                        "finding_ref": loser_ref,
                    }
                )
            )

    return deduped_primaries + secondaries + demoted


def _dedupe_cross_category_overlaps(
    findings: list[RuleFinding],
    *,
    audit_id: uuid.UUID | str | None,
) -> list[RuleFinding]:
    """Collapse primaries that quantify the same monthly leakage under different rule explanations."""
    findings = _dedupe_primaries_by_key(
        findings,
        _invoice_monthly_key,
        audit_id=audit_id,
        suffix="overlap-invoice",
    )
    return _dedupe_primaries_by_key(
        findings,
        _subscription_product_monthly_key,
        audit_id=audit_id,
        suffix="overlap-subscription",
    )


def attribute_findings(
    findings: list[RuleFinding],
    *,
    audit_id: uuid.UUID | str | None = None,
) -> list[RuleFinding]:
    if not findings:
        return []

    within_family = _attribute_within_family(findings, audit_id=audit_id)
    return _dedupe_cross_category_overlaps(within_family, audit_id=audit_id)


def sum_primary_recoverable_arr(findings: list[RuleFinding] | list) -> Decimal:
    total = Decimal("0")
    for finding in findings:
        if getattr(finding, "attribution", "primary") != "primary":
            continue
        total += finding_recoverable_amount(finding)
    return total.quantize(Decimal("0.0001"))


def sum_secondary_excluded_arr(findings: list[RuleFinding] | list) -> Decimal:
    total = Decimal("0")
    for finding in findings:
        if getattr(finding, "attribution", "primary") != "secondary":
            continue
        total += finding_recoverable_amount(finding)
    return total.quantize(Decimal("0.0001"))


def primary_findings(findings: list) -> list:
    return [finding for finding in findings if getattr(finding, "attribution", "primary") == "primary"]
