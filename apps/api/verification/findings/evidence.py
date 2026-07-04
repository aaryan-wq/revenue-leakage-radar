from __future__ import annotations

import hashlib

from verification.types import EvidenceInput, EvidenceRecord


def build_evidence(inputs: list[EvidenceInput]) -> list[EvidenceRecord]:
    return [
        EvidenceRecord(
            field=item.field,
            expected=item.expected,
            actual=item.actual,
            reference_ids=dict(item.reference_ids),
        )
        for item in inputs
    ]


def trace_evidence_from_calculation(trace) -> list[EvidenceRecord]:
    records: list[EvidenceRecord] = []
    for step in trace.steps:
        records.append(
            EvidenceRecord(
                field=step.step_id,
                expected=str(step.value),
                actual=str(step.value),
                reference_ids=dict(step.source_refs),
            )
        )
    return records
