"""Differential verification: compare engine findings against ground truth."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from decimal import Decimal

from harness.context_loader import IdMaps
from harness.types import GroundTruthFinding
from verification.types import RuleFinding


@dataclass
class FindingMismatch:
    rule_id: str
    kind: str
    message: str
    expected: GroundTruthFinding | None = None
    actual: RuleFinding | None = None


@dataclass
class ComparisonResult:
    passed: bool
    expected_count: int
    actual_count: int
    matched: int
    mismatches: list[FindingMismatch] = field(default_factory=list)

    def summary(self) -> str:
        if self.passed:
            return f"PASS: {self.matched}/{self.expected_count} findings matched"
        lines = [f"FAIL: {len(self.mismatches)} mismatches ({self.matched}/{self.expected_count} matched)"]
        for mismatch in self.mismatches[:10]:
            lines.append(f"  [{mismatch.kind}] {mismatch.rule_id}: {mismatch.message}")
        if len(self.mismatches) > 10:
            lines.append(f"  ... and {len(self.mismatches) - 10} more")
        return "\n".join(lines)


def _external_customer_id(customer_uuid: str | None, id_maps: IdMaps, reverse_customer: dict[uuid.UUID, str]) -> str | None:
    if not customer_uuid:
        return None
    try:
        uid = uuid.UUID(str(customer_uuid))
    except ValueError:
        return customer_uuid
    return reverse_customer.get(uid)


def _external_subscription_id(sub_uuid: str | None, reverse_sub: dict[uuid.UUID, str]) -> str | None:
    if not sub_uuid:
        return None
    try:
        uid = uuid.UUID(str(sub_uuid))
    except ValueError:
        return sub_uuid
    return reverse_sub.get(uid)


def _external_invoice_id(inv_uuid: str | None, reverse_inv: dict[uuid.UUID, str]) -> str | None:
    if not inv_uuid:
        return None
    try:
        uid = uuid.UUID(str(inv_uuid))
    except ValueError:
        return inv_uuid
    return reverse_inv.get(uid)


def _finding_key(
    rule_id: str,
    customer_id: str | None,
    subscription_id: str | None,
    invoice_id: str | None,
) -> tuple:
    return (rule_id, customer_id or "", subscription_id or "", invoice_id or "")


def _actual_to_external(finding: RuleFinding, id_maps: IdMaps) -> tuple[str | None, str | None, str | None]:
    reverse_customer = {v: k for k, v in id_maps.customer.items()}
    reverse_sub = {v: k for k, v in id_maps.subscription.items()}
    reverse_inv = {v: k for k, v in id_maps.invoice.items()}
    return (
        _external_customer_id(finding.customer_id, id_maps, reverse_customer),
        _external_subscription_id(finding.subscription_id, reverse_sub),
        _external_invoice_id(finding.invoice_id, reverse_inv),
    )


def _amounts_match(expected: Decimal, actual: Decimal) -> bool:
    return abs(expected.quantize(Decimal("0.0001")) - actual.quantize(Decimal("0.0001"))) <= Decimal("0.01")


def compare_findings(
    ground_truth: list[GroundTruthFinding],
    actual_findings: list[RuleFinding],
    id_maps: IdMaps,
    *,
    allow_extra: bool = False,
) -> ComparisonResult:
    positives = [g for g in ground_truth if not g.is_negative]
    negatives = [g for g in ground_truth if g.is_negative]

    actual_by_key: dict[tuple, list[RuleFinding]] = {}
    for finding in actual_findings:
        cust, sub, inv = _actual_to_external(finding, id_maps)
        key = _finding_key(finding.rule_id, cust, sub, inv)
        actual_by_key.setdefault(key, []).append(finding)

    matched = 0
    mismatches: list[FindingMismatch] = []
    used_actual: set[int] = set()

    for expected in positives:
        key = _finding_key(
            expected.rule_id,
            expected.customer_id,
            expected.subscription_id,
            expected.invoice_id,
        )
        candidates = actual_by_key.get(key, [])

        if not candidates:
            loose_key = (expected.rule_id, expected.customer_id or "", expected.subscription_id or "", "")
            candidates = actual_by_key.get(loose_key, [])

        if not candidates and expected.subscription_id:
            rule_candidates = [
                f
                for f in actual_findings
                if f.rule_id == expected.rule_id
                and id(f) not in used_actual
                and _external_subscription_id(f.subscription_id, {v: k for k, v in id_maps.subscription.items()})
                == expected.subscription_id
            ]
            candidates = rule_candidates

        if not candidates:
            amount_matches = [
                f
                for f in actual_findings
                if f.rule_id == expected.rule_id
                and id(f) not in used_actual
                and _amounts_match(expected.expected_monthly_leakage, f.estimated_monthly_loss)
                and _amounts_match(expected.expected_annual_leakage, f.estimated_arr_loss)
            ]
            if amount_matches:
                candidates = amount_matches

        if not candidates:
            mismatches.append(
                FindingMismatch(
                    rule_id=expected.rule_id,
                    kind="missing",
                    message=(
                        f"No finding for customer={expected.customer_id} "
                        f"sub={expected.subscription_id} inv={expected.invoice_id}"
                    ),
                    expected=expected,
                )
            )
            continue

        actual = candidates[0]
        used_actual.add(id(actual))

        if not _amounts_match(expected.expected_monthly_leakage, actual.estimated_monthly_loss):
            mismatches.append(
                FindingMismatch(
                    rule_id=expected.rule_id,
                    kind="monthly_mismatch",
                    message=(
                        f"monthly expected={expected.expected_monthly_leakage} "
                        f"actual={actual.estimated_monthly_loss}"
                    ),
                    expected=expected,
                    actual=actual,
                )
            )
            continue

        if not _amounts_match(expected.expected_annual_leakage, actual.estimated_arr_loss):
            mismatches.append(
                FindingMismatch(
                    rule_id=expected.rule_id,
                    kind="annual_mismatch",
                    message=(
                        f"annual expected={expected.expected_annual_leakage} "
                        f"actual={actual.estimated_arr_loss}"
                    ),
                    expected=expected,
                    actual=actual,
                )
            )
            continue

        if expected.expected_severity and actual.severity != expected.expected_severity:
            mismatches.append(
                FindingMismatch(
                    rule_id=expected.rule_id,
                    kind="severity_mismatch",
                    message=f"severity expected={expected.expected_severity} actual={actual.severity}",
                    expected=expected,
                    actual=actual,
                )
            )
            continue

        matched += 1

    for negative in negatives:
        key = _finding_key(
            negative.rule_id,
            negative.customer_id,
            negative.subscription_id,
            negative.invoice_id,
        )
        if actual_by_key.get(key):
            mismatches.append(
                FindingMismatch(
                    rule_id=negative.rule_id,
                    kind="false_positive",
                    message=f"Unexpected finding for negative case key={key}",
                    expected=negative,
                    actual=actual_by_key[key][0],
                )
            )

    if not allow_extra:
        matched_ids = used_actual
        for finding in actual_findings:
            if id(finding) in matched_ids:
                continue
            cust, sub, inv = _actual_to_external(finding, id_maps)
            expected_rules = {g.rule_id for g in positives}
            if finding.rule_id in expected_rules:
                continue
            mismatches.append(
                FindingMismatch(
                    rule_id=finding.rule_id,
                    kind="unexpected",
                    message=f"Unexpected finding customer={cust} sub={sub}",
                    actual=finding,
                )
            )

    return ComparisonResult(
        passed=len(mismatches) == 0,
        expected_count=len(positives),
        actual_count=len(actual_findings),
        matched=matched,
        mismatches=mismatches,
    )
