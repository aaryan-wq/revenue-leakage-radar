export type AuditStatus =
  | "created"
  | "uploading"
  | "mapping"
  | "validating"
  | "normalizing"
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
