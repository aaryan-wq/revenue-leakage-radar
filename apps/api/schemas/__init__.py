import uuid
from datetime import datetime

from pydantic import BaseModel, Field

from core.enums import AuditStatus, FileType, UploadStatus


class HealthResponse(BaseModel):
    status: str = "ok"
    version: str = "0.1.0"


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


class ErrorResponse(BaseModel):
    detail: str
