import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from core.enums import AuditStatus, FileType, Platform, UploadStatus, ValidationResult


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.2.0"


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


class AuditStatusResponse(BaseModel):
    audit_id: uuid.UUID
    status: AuditStatus
    uploads: list[UploadResponse]
    required_files_present: bool
    missing_file_types: list[FileType] = Field(default_factory=list)
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
