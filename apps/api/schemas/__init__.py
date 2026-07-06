import uuid
from datetime import datetime
from typing import Any

from core.canonical_entities import CanonicalEntity
from pydantic import BaseModel, Field

from core.enums import AuditStatus, DataTier, FileType, Platform, UploadStatus, ValidationResult


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.2.0"
    database: bool | None = None
    redis: bool | None = None


class AuditCreateResponse(BaseModel):
    audit_id: uuid.UUID
    session_token: str
    status: AuditStatus


class UploadResponse(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    file_type: FileType
    original_filename: str
    file_size: int
    status: UploadStatus
    created_at: datetime


class CoverageCategoryScore(BaseModel):
    category: str
    label: str
    score: int


class UnavailableRule(BaseModel):
    name: str
    reason: str


class AvailableRule(BaseModel):
    name: str
    status: str
    note: str | None = None


class UnlockHint(BaseModel):
    file_type: str
    label: str
    rules_unlocked: int


class CoverageAnalysis(BaseModel):
    billing_data_received: list[str] = Field(default_factory=list)
    rules_available: int = 0
    rules_total: int = 0
    available_rules: list[AvailableRule] = Field(default_factory=list)
    unavailable_rules: list[UnavailableRule] = Field(default_factory=list)
    estimated_confidence: int = 0
    category_scores: list[CoverageCategoryScore] = Field(default_factory=list)
    unlock_hints: list[UnlockHint] = Field(default_factory=list)


class AuditStatusResponse(BaseModel):
    audit_id: uuid.UUID
    status: AuditStatus
    uploads: list[UploadResponse]
    required_files_present: bool
    has_billing_upload: bool = False
    tier_0_complete: bool = False
    missing_file_types: list[FileType] = Field(default_factory=list)
    missing_recommended_file_types: list[FileType] = Field(default_factory=list)
    available_entities: list[CanonicalEntity] = Field(default_factory=list)
    missing_entities: list[CanonicalEntity] = Field(default_factory=list)
    data_tier: DataTier = DataTier.INSUFFICIENT
    coverage_analysis: CoverageAnalysis | None = None
    platform: str | None = None
    validation_result: ValidationResult | None = None
    can_proceed_to_scan: bool = False
    ingestion_error: str | None = None


class ValidateResponse(BaseModel):
    audit_id: uuid.UUID
    status: AuditStatus
    message: str


class ValidationIssueResponse(BaseModel):
    severity: str
    code: str
    message: str
    file_type: str | None = None
    field: str | None = None
    row: int | None = None


class ValidationReportResponse(BaseModel):
    audit_id: uuid.UUID
    status: AuditStatus
    platform: Platform | None = None
    column_mappings: dict[str, dict[str, str]] = Field(default_factory=dict)
    validation_result: ValidationResult | None = None
    validation_report: dict[str, Any] = Field(default_factory=dict)
    ingestion_error: str | None = None
    can_proceed_to_scan: bool = False
    summary: dict[str, Any] = Field(default_factory=dict)


class ErrorResponse(BaseModel):
    detail: str


class ScanResponse(BaseModel):
    audit_id: uuid.UUID
    status: AuditStatus
    message: str


class ScanReportResponse(BaseModel):
    audit_id: uuid.UUID
    status: AuditStatus
    scan_report: dict[str, Any] = Field(default_factory=dict)
    scan_error: str | None = None
    finding_count: int = 0
    recoverable_arr: str = "0"
    rules_completed: int = 0
    rules_total: int = 0
    overall_confidence: str | None = None


class OpportunityBreakdownItem(BaseModel):
    category: str
    label: str
    arr: str
    confidence: str | None = None
    issue_count: int
    account_count: int = 0


class VerificationCheckItem(BaseModel):
    rule_id: str
    name: str
    status: str
    finding_count: int = 0
    arr: str = "0"
    skip_reason: str | None = None
    coverage_note: str | None = None


class LockedPreviewItem(BaseModel):
    title: str
    category: str
    category_label: str
    arr: str


class SummaryCoverage(BaseModel):
    data_tier: str
    billing_files_uploaded: list[str]
    billing_files_missing: list[str]
    crm_files_uploaded: list[str]
    crm_present: bool
    confidence_impact: str


class FreeSummaryResponse(BaseModel):
    audit_id: uuid.UUID
    report_id: uuid.UUID
    recoverable_arr: str
    confidence: str | None = None
    finding_count: int
    accounts_reviewed: int
    invoices_reviewed: int
    rules_completed: int
    rules_total: int
    opportunity_breakdown: list[OpportunityBreakdownItem]
    verification_checks: list[VerificationCheckItem]
    locked_preview: list[LockedPreviewItem]
    coverage: SummaryCoverage
    purchased: bool
    generated_at: str | None = None


class EvidenceRecordResponse(BaseModel):
    field: str
    expected: str | None = None
    actual: str | None = None
    reference_ids: dict[str, str] = Field(default_factory=dict)


class CalculationStepResponse(BaseModel):
    step_id: str
    label: str
    value: str
    unit: str | None = None
    source_refs: dict[str, str] = Field(default_factory=dict)


class CalculationTraceResponse(BaseModel):
    steps: list[CalculationStepResponse] = Field(default_factory=list)
    result_monthly: str
    result_annual: str
    semantics: str


class FindingResponse(BaseModel):
    id: uuid.UUID
    rule_id: str
    title: str
    category: str
    category_label: str
    severity: str
    confidence: str
    customer_id: str | None = None
    subscription_id: str | None = None
    invoice_id: str | None = None
    estimated_monthly_loss: str
    estimated_arr_loss: str
    recoverable_amount: str | None = None
    recommendation: str | None = None
    attribution: str | None = None
    leak_family: str | None = None
    finding_ref: str | None = None
    primary_finding_ref: str | None = None
    primary_finding_id: uuid.UUID | None = None
    primary_finding_title: str | None = None
    leakage_computation: dict[str, Any] | None = None
    leakage_semantics: str | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    evidence_records: list[EvidenceRecordResponse] = Field(default_factory=list)
    calculation_trace: CalculationTraceResponse | None = None


class ExecutiveSummaryResponse(BaseModel):
    recoverable_arr: str
    high_confidence_arr: str
    medium_confidence_arr: str
    low_confidence_arr: str
    accounts_reviewed: int
    invoices_reviewed: int
    finding_count: int
    confidence: str | None = None
    rules_completed: int
    rules_total: int
    narrative: str


class ReportDetailResponse(BaseModel):
    id: uuid.UUID
    audit_id: uuid.UUID
    purchased: bool
    generated_at: str | None = None
    company_name: str | None = None
    executive_summary: ExecutiveSummaryResponse
    opportunity_breakdown: list[OpportunityBreakdownItem]
    verification_checks: list[VerificationCheckItem]
    findings_total: int = 0
    locked_preview: list[LockedPreviewItem] = Field(default_factory=list)
    findings: list[FindingResponse] = Field(default_factory=list)


class PaginatedFindingsResponse(BaseModel):
    items: list[FindingResponse]
    total: int
    page: int
    page_size: int
    has_more: bool


class FindingDetailResponse(FindingResponse):
    audit_id: uuid.UUID
    report_id: uuid.UUID


class ReportListItem(BaseModel):
    audit_id: uuid.UUID
    report_id: uuid.UUID
    date: str | None = None
    recoverable_arr: str
    status: str
    finding_count: int
    purchased: bool
    company_name: str | None = None


class DashboardResponse(BaseModel):
    company_name: str | None = None
    reports_remaining: int = 0
    audits: list[ReportListItem]


class UnlockReportResponse(BaseModel):
    report_id: uuid.UUID
    purchased: bool
    message: str
