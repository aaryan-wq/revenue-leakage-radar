import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AdminMeResponse(BaseModel):
    is_admin: bool = True
    email: str | None = None


class AdminOverviewResponse(BaseModel):
    total_audits: int
    linked_users: int
    total_reports: int
    purchased_reports: int
    total_purchases: int
    total_recoverable_arr: str
    audits_last_7_days: int
    purchases_last_7_days: int


class AdminCompanyItem(BaseModel):
    id: uuid.UUID
    name: str
    audit_count: int
    created_at: datetime | None


class PaginatedCompaniesResponse(BaseModel):
    items: list[AdminCompanyItem]
    total: int
    page: int
    page_size: int


class AdminAuditListItem(BaseModel):
    audit_id: uuid.UUID
    report_id: uuid.UUID | None
    company_name: str | None
    clerk_user_id: str | None
    status: str
    recoverable_arr: str | None
    finding_count: int | None
    purchased: bool
    created_at: datetime | None
    verification_completed_at: datetime | None


class PaginatedAuditsResponse(BaseModel):
    items: list[AdminAuditListItem]
    total: int
    page: int
    page_size: int


class AdminUploadItem(BaseModel):
    id: uuid.UUID
    file_type: str
    original_filename: str
    file_size: int
    status: str
    created_at: datetime | None


class AdminPurchaseItem(BaseModel):
    id: uuid.UUID
    plan: str
    amount_cents: int | None
    currency: str | None
    status: str
    stripe_payment_intent_id: str | None
    created_at: datetime | None


class AdminAuditDetailResponse(BaseModel):
    audit_id: uuid.UUID
    report_id: uuid.UUID | None
    company_name: str | None
    company_id: uuid.UUID | None
    clerk_user_id: str | None
    status: str
    platform: str | None
    recoverable_arr: str | None
    finding_count: int | None
    purchased: bool
    ingestion_error: str | None
    scan_error: str | None
    created_at: datetime | None
    verification_completed_at: datetime | None
    uploads: list[AdminUploadItem]
    purchases: list[AdminPurchaseItem]


class AdminReportListItem(BaseModel):
    report_id: uuid.UUID
    audit_id: uuid.UUID
    company_name: str | None
    clerk_user_id: str | None
    recoverable_arr: str
    finding_count: int
    purchased: bool
    status: str
    generated_at: datetime | None


class PaginatedReportsResponse(BaseModel):
    items: list[AdminReportListItem]
    total: int
    page: int
    page_size: int


class AdminLogEntry(BaseModel):
    id: str
    timestamp: datetime
    log_type: str
    entity_type: str | None
    entity_id: str | None
    message: str
    metadata: dict | None = None


class PaginatedLogsResponse(BaseModel):
    items: list[AdminLogEntry]
    total: int
    page: int
    page_size: int


class AdminReprocessRequest(BaseModel):
    audit_id: uuid.UUID


class AdminReprocessResponse(BaseModel):
    audit_id: uuid.UUID
    status: str
    message: str


class AdminRefundRequest(BaseModel):
    purchase_id: uuid.UUID
    reason: str | None = Field(default=None, max_length=500)


class AdminRefundResponse(BaseModel):
    purchase_id: uuid.UUID
    status: str
    message: str


class SupportNoteCreateRequest(BaseModel):
    entity_type: str = Field(min_length=1, max_length=32)
    entity_id: str = Field(min_length=1, max_length=255)
    body: str = Field(min_length=1, max_length=10000)


class SupportNoteResponse(BaseModel):
    id: uuid.UUID
    entity_type: str
    entity_id: str
    author_clerk_user_id: str
    body: str
    created_at: datetime
    updated_at: datetime


class PaginatedSupportNotesResponse(BaseModel):
    items: list[SupportNoteResponse]
    total: int
    page: int
    page_size: int
