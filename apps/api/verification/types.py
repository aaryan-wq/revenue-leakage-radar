from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field


class EvidenceRecord(BaseModel):
    field: str
    expected: str | None = None
    actual: str | None = None
    reference_ids: dict[str, str] = Field(default_factory=dict)


class RuleFinding(BaseModel):
    rule_id: str
    title: str
    severity: str
    confidence: Decimal
    customer_id: str | None = None
    subscription_id: str | None = None
    invoice_id: str | None = None
    expected_value: Decimal | None = None
    actual_value: Decimal | None = None
    delta: Decimal | None = None
    estimated_monthly_loss: Decimal = Decimal("0")
    estimated_arr_loss: Decimal = Decimal("0")
    recommendation: str
    evidence: list[EvidenceRecord] = Field(default_factory=list)

    def evidence_json(self) -> dict[str, Any]:
        return {
            "expected_value": str(self.expected_value) if self.expected_value is not None else None,
            "actual_value": str(self.actual_value) if self.actual_value is not None else None,
            "delta": str(self.delta) if self.delta is not None else None,
            "records": [r.model_dump() for r in self.evidence],
        }


class RuleExecutionLog(BaseModel):
    rule_id: str
    status: str  # ran | skipped | error
    finding_count: int = 0
    duration_ms: int = 0
    skip_reason: str | None = None
    error: str | None = None


class ScanReport(BaseModel):
    rules_total: int = 0
    rules_completed: int = 0
    rules_skipped: int = 0
    finding_count: int = 0
    recoverable_arr: str = "0"
    overall_confidence: str | None = None
    rule_logs: list[RuleExecutionLog] = Field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return self.model_dump()
