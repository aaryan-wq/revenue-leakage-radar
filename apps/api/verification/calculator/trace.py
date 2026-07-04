from __future__ import annotations

from decimal import Decimal

from pydantic import BaseModel, Field


class CalculationStep(BaseModel):
    step_id: str
    label: str
    value: Decimal
    unit: str | None = None
    source_refs: dict[str, str] = Field(default_factory=dict)


class CalculationTrace(BaseModel):
    steps: list[CalculationStep] = Field(default_factory=list)
    result_monthly: Decimal = Decimal("0")
    result_annual: Decimal = Decimal("0")
    semantics: str = "recurring_run_rate"

    def trace_hash_input(self) -> str:
        parts = [f"{step.step_id}:{step.value}" for step in self.steps]
        parts.append(f"monthly:{self.result_monthly}")
        parts.append(f"annual:{self.result_annual}")
        return "|".join(parts)


class TraceBuilder:
    def __init__(self, semantics: str = "recurring_run_rate") -> None:
        self._steps: list[CalculationStep] = []
        self._semantics = semantics

    def add(
        self,
        step_id: str,
        label: str,
        value: Decimal,
        *,
        unit: str | None = None,
        source_refs: dict[str, str] | None = None,
    ) -> TraceBuilder:
        self._steps.append(
            CalculationStep(
                step_id=step_id,
                label=label,
                value=value.quantize(Decimal("0.0001")),
                unit=unit,
                source_refs=source_refs or {},
            )
        )
        return self

    def finish(self, monthly: Decimal, annual: Decimal) -> CalculationTrace:
        return CalculationTrace(
            steps=list(self._steps),
            result_monthly=monthly.quantize(Decimal("0.0001")),
            result_annual=annual.quantize(Decimal("0.0001")),
            semantics=self._semantics,
        )
