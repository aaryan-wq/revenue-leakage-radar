import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class AdminMeResponse(BaseModel):
    is_admin: bool = True
    email: str | None = None


class AdminOverviewResponse(BaseModel):
    total_audits: int
    linked_users: int
    anonymous_audits: int
    completed_audits: int
    audits_in_progress: int
    total_reports: int
    purchased_reports: int
    total_purchases: int
    refunded_purchases: int
    total_recoverable_arr: str
    average_recoverable_arr: str
    total_purchase_revenue_cents: int
    audits_last_7_days: int
    audits_last_30_days: int
    purchases_last_7_days: int
    purchases_last_30_days: int
    total_companies: int
    active_memberships: int
    purchase_conversion_pct: float
    total_assessments: int
    completed_assessments: int
    assessments_last_7_days: int
    assessments_last_30_days: int
    assessments_with_leads: int
    assessments_scan_intent: int
    assessments_linked_to_audits: int
    assessment_to_audit_conversion_pct: float


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


class AdminAccountListItem(BaseModel):
    clerk_user_id: str
    clerk_user_name: str | None = None
    clerk_user_email: str | None = None
    plan: str | None
    membership_status: str | None
    reports_remaining: int | None
    audit_count: int
    purchase_count: int
    joined_at: datetime | None
    last_active_at: datetime | None


class PaginatedAccountsResponse(BaseModel):
    items: list[AdminAccountListItem]
    total: int
    page: int
    page_size: int


class AdminAuditListItem(BaseModel):
    audit_id: uuid.UUID
    report_id: uuid.UUID | None
    company_name: str | None
    clerk_user_id: str | None
    clerk_user_name: str | None = None
    clerk_user_email: str | None = None
    assessment_id: uuid.UUID | None = None
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
    clerk_user_name: str | None = None
    clerk_user_email: str | None = None
    assessment_id: uuid.UUID | None = None
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
    clerk_user_name: str | None = None
    clerk_user_email: str | None = None
    recoverable_arr: str
    finding_count: int
    purchased: bool
    status: str
    generated_at: datetime | None


class AdminAssessmentListItem(BaseModel):
    assessment_id: uuid.UUID
    status: str
    industry: str | None
    country: str | None
    arr_amount: str | None
    arr_currency: str | None
    customer_count: int | None
    estimated_leakage: str | None
    lead_email: str | None
    lead_company_name: str | None
    lead_role: str | None
    lead_score: int | None
    scan_intent: bool
    linked_audit_id: uuid.UUID | None
    clerk_user_id: str | None
    clerk_user_name: str | None = None
    clerk_user_email: str | None = None
    started_at: datetime | None
    completed_at: datetime | None
    created_at: datetime | None


class PaginatedAssessmentsResponse(BaseModel):
    items: list[AdminAssessmentListItem]
    total: int
    page: int
    page_size: int


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
