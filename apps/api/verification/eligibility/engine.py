from __future__ import annotations

from dataclasses import dataclass

from verification.eligibility.schema import EligibilityStatus, FieldRequirement, RuleSpec
from verification.context import CanonicalContext


@dataclass
class EligibilityResult:
    status: EligibilityStatus
    missing_required: list[FieldRequirement]
    missing_optional: list[FieldRequirement]
    skip_reason: str | None = None

    @property
    def is_runnable(self) -> bool:
        return self.status in ("runnable", "partial")


def _format_fields(fields: list[FieldRequirement]) -> str:
    return ", ".join(f"{field.entity.value}.{field.field}" for field in fields)


def resolve_eligibility(spec: RuleSpec, ctx: CanonicalContext) -> EligibilityResult:
    availability = ctx.field_availability()
    missing_required = [req for req in spec.required_fields if req.key() not in availability]
    if missing_required:
        return EligibilityResult(
            status="skipped",
            missing_required=missing_required,
            missing_optional=[],
            skip_reason=f"Missing required fields: {_format_fields(missing_required)}",
        )

    missing_optional = [req for req in spec.optional_fields if req.key() not in availability]
    if spec.eligibility_conditions is not None:
        ok, reason = spec.eligibility_conditions(ctx)
        if not ok:
            return EligibilityResult(
                status="skipped",
                missing_required=[],
                missing_optional=missing_optional,
                skip_reason=reason or "Eligibility conditions not met",
            )

    if missing_optional:
        return EligibilityResult(
            status="partial",
            missing_required=[],
            missing_optional=missing_optional,
            skip_reason=f"Running with reduced coverage; missing: {_format_fields(missing_optional)}",
        )

    return EligibilityResult(
        status="runnable",
        missing_required=[],
        missing_optional=[],
    )
