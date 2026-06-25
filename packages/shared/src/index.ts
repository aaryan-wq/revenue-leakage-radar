export type AuditStatus =
  | "created"
  | "uploading"
  | "mapping"
  | "validating"
  | "normalizing"
  | "ready_for_scan"
  | "scanning"
  | "generating_report"
  | "completed"
  | "upload_failed"
  | "validation_failed"
  | "processing_failed"
  | "payment_pending";

export type FileType =
  | "subscriptions"
  | "invoices"
  | "invoice_line_items"
  | "coupons"
  | "price_catalog"
  | "crm_accounts"
  | "crm_opportunities"
  | "crm_contracts"
  | "unknown";

export type UploadStatus = "pending" | "uploading" | "uploaded" | "failed";

export type Platform = "stripe" | "chargebee" | "maxio" | "zuora" | "generic";

export type ValidationResult = "ready" | "warnings" | "blocking";

export const PROCESSING_STATUSES: AuditStatus[] = [
  "mapping",
  "validating",
  "normalizing",
];

export const SCAN_PROCESSING_STATUSES: AuditStatus[] = [
  "scanning",
  "generating_report",
];

export interface RuleExecutionStatus {
  rule_id: string;
  status: "ran" | "skipped" | "error";
  finding_count?: number;
  duration_ms?: number;
  skip_reason?: string | null;
  error?: string | null;
}

export interface ScanReportResponse {
  audit_id: string;
  status: AuditStatus;
  scan_report: {
    rules_total?: number;
    rules_completed?: number;
    rules_skipped?: number;
    finding_count?: number;
    recoverable_arr?: string;
    overall_confidence?: string | null;
    rule_logs?: RuleExecutionStatus[];
  };
  scan_error?: string | null;
  finding_count: number;
  recoverable_arr: string;
  rules_completed: number;
  rules_total: number;
  overall_confidence?: string | null;
}

export interface ScanResponse {
  audit_id: string;
  status: AuditStatus;
  message: string;
}

export interface AuditCreateResponse {
  audit_id: string;
  session_token: string;
  status: AuditStatus;
}

export interface UploadResponse {
  id: string;
  audit_id: string;
  file_type: FileType;
  original_filename: string;
  file_size: number;
  status: UploadStatus;
  created_at: string;
}

export interface AuditStatusResponse {
  audit_id: string;
  status: AuditStatus;
  uploads: UploadResponse[];
  required_files_present: boolean;
  missing_file_types: FileType[];
  platform?: string | null;
  validation_result?: ValidationResult | null;
  can_proceed_to_scan?: boolean;
  ingestion_error?: string | null;
}

export interface ValidationIssue {
  severity: "blocking" | "warning";
  code: string;
  message: string;
  file_type?: string | null;
  field?: string | null;
  row?: number | null;
}

export interface ValidationReportResponse {
  audit_id: string;
  status: AuditStatus;
  platform?: Platform | null;
  column_mappings: Record<string, Record<string, string>>;
  validation_result?: ValidationResult | null;
  validation_report: {
    issues?: ValidationIssue[];
    row_errors?: Array<Record<string, unknown>>;
    summary?: Record<string, unknown>;
    canonical_counts?: Record<string, number>;
  };
  ingestion_error?: string | null;
  can_proceed_to_scan: boolean;
  summary: {
    blocking_count?: number;
    warning_count?: number;
    issue_count?: number;
  };
}

export interface ValidateResponse {
  audit_id: string;
  status: AuditStatus;
  message: string;
}

export const REQUIRED_BILLING_FILES: FileType[] = [
  "subscriptions",
  "invoices",
  "invoice_line_items",
  "coupons",
  "price_catalog",
];

export const FILE_TYPE_LABELS: Record<FileType, string> = {
  subscriptions: "Subscriptions",
  invoices: "Invoices",
  invoice_line_items: "Invoice Line Items",
  coupons: "Coupons",
  price_catalog: "Price Catalog",
  crm_accounts: "CRM Accounts",
  crm_opportunities: "CRM Opportunities",
  crm_contracts: "CRM Contracts",
  unknown: "Unknown",
};

export const PLATFORM_LABELS: Record<Platform, string> = {
  stripe: "Stripe",
  chargebee: "Chargebee",
  maxio: "Maxio",
  zuora: "Zuora",
  generic: "Generic",
};
