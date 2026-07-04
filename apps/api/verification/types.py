from __future__ import annotations

from decimal import Decimal
from typing import Any, Literal

from pydantic import BaseModel, Field

from verification.calculator.trace import CalculationTrace

LeakageSemantics = Literal["recurring_run_rate", "per_period", "one_time", "operational"]
LeakFamily = Literal[
    "subscription_pricing_gap",
    "discount_integrity",
    "invoice_execution",
    "renewal_event",
    "usage_monetization",
    "operational",
]
Attribution = Literal["primary", "secondary"]
Severity = Literal["high", "medium", "low"]
FindingStatus = Literal["open"]


class LeakageComputation(BaseModel):
    """Backward-compatible computation summary for report UI."""

    semantics: LeakageSemantics
    unit_expected: Decimal
    unit_actual: Decimal
    quantity: int
    billing_interval: str
    monthly_loss: Decimal
    annual_loss: Decimal
    formula: str


class EvidenceRecord(BaseModel):
    field: str
    expected: str | None = None
    actual: str | None = None
    reference_ids: dict[str, str] = Field(default_factory=dict)


class RuleScope(BaseModel):
    customer_id: str | None = None
    subscription_id: str | None = None
    invoice_id: str | None = None
    product_id: str | None = None


class EvidenceInput(BaseModel):
    field: str
    expected: str | None = None
    actual: str | None = None
    reference_ids: dict[str, str] = Field(default_factory=dict)


class RuleResult(BaseModel):
    scope: RuleScope
    expected_value: Decimal | None = None
    actual_value: Decimal | None = None
    difference: Decimal | None = None
    calculation: CalculationTrace
    evidence_fields: list[EvidenceInput] = Field(default_factory=list)
    confidence: Decimal
    severity: Severity
    recommendation: str | None = None


class RuleFinding(BaseModel):
    rule_id: str
    rule_name: str
    title: str
    severity: Severity
    confidence: Decimal
    status: FindingStatus = "open"
    customer_id: str | None = None
    subscription_id: str | None = None
    invoice_id: str | None = None
    product_id: str | None = None
    expected_value: Decimal | None = None
    actual_value: Decimal | None = None
    delta: Decimal | None = None
    estimated_monthly_loss: Decimal = Decimal("0")
    estimated_arr_loss: Decimal = Decimal("0")
    recommendation: str
    evidence: list[EvidenceRecord] = Field(default_factory=list)
    calculation_trace: CalculationTrace | None = None
    leak_family: LeakFamily | None = None
    leakage_computation: LeakageComputation | None = None
    attribution: Attribution = "primary"
    finding_ref: str | None = None
    primary_finding_ref: str | None = None
    rule_version: str = "2.0.0"

    def evidence_json(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "rule_name": self.rule_name,
            "expected_value": str(self.expected_value) if self.expected_value is not None else None,
            "actual_value": str(self.actual_value) if self.actual_value is not None else None,
            "delta": str(self.delta) if self.delta is not None else None,
            "leak_family": self.leak_family,
            "attribution": self.attribution,
            "finding_ref": self.finding_ref,
            "primary_finding_ref": self.primary_finding_ref,
            "status": self.status,
            "rule_version": self.rule_version,
            "records": [record.model_dump() for record in self.evidence],
        }
        if self.calculation_trace is not None:
            payload["calculation_trace"] = self.calculation_trace.model_dump(mode="json")
        if self.leakage_computation is not None:
            payload["leakage_computation"] = self.leakage_computation.model_dump(mode="json")
        return payload


class RuleExecutionLog(BaseModel):
    rule_id: str
    status: str
    finding_count: int = 0
    duration_ms: int = 0
    skip_reason: str | None = None
    error: str | None = None
    coverage_note: str | None = None


class ScanReport(BaseModel):
    rules_total: int = 0
    rules_completed: int = 0
    rules_skipped: int = 0
    rules_partial: int = 0
    rules_errored: int = 0
    finding_count: int = 0
    recoverable_arr: str = "0"
    overall_confidence: str | None = None
    data_tier: str | None = None
    rule_logs: list[RuleExecutionLog] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
