/** Canonical entities produced by ingestion (CEM). */
export type CanonicalEntity =
  | "customer"
  | "subscription"
  | "invoice"
  | "invoice_line_item"
  | "price"
  | "coupon"
  | "contract"
  | "account"
  | "opportunity";

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

export type DataTier = "insufficient" | "tier_0" | "tier_1" | "tier_2_plus";

export type FileType =
  | "customers"
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
  status: "ran" | "skipped" | "partial" | "error";
  finding_count?: number;
  duration_ms?: number;
  skip_reason?: string | null;
  coverage_note?: string | null;
  error?: string | null;
}

export interface ScanReportResponse {
  audit_id: string;
  status: AuditStatus;
  scan_report: {
    rules_total?: number;
    rules_completed?: number;
    rules_skipped?: number;
    rules_partial?: number;
    rules_errored?: number;
    finding_count?: number;
    recoverable_arr?: string;
    overall_confidence?: string | null;
    data_tier?: DataTier | string | null;
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
  /** @deprecated Use has_billing_upload, true when at least one billing export is uploaded. */
  required_files_present: boolean;
  has_billing_upload: boolean;
  tier_0_complete: boolean;
  missing_file_types: FileType[];
  missing_recommended_file_types: FileType[];
  available_entities: CanonicalEntity[];
  missing_entities: CanonicalEntity[];
  data_tier: DataTier;
  coverage_analysis?: CoverageAnalysis | null;
  platform?: string | null;
  validation_result?: ValidationResult | null;
  can_proceed_to_scan?: boolean;
  ingestion_error?: string | null;
}

export interface CoverageCategoryScore {
  category: string;
  label: string;
  score: number;
}

export interface UnavailableRule {
  name: string;
  reason: string;
}

export interface AvailableRule {
  name: string;
  status: "available" | "partial";
  note?: string | null;
}

export interface UnlockHint {
  file_type: string;
  label: string;
  rules_unlocked: number;
}

export interface CoverageAnalysis {
  billing_data_received: string[];
  rules_available: number;
  rules_total: number;
  available_rules: AvailableRule[];
  unavailable_rules: UnavailableRule[];
  estimated_confidence: number;
  category_scores: CoverageCategoryScore[];
  unlock_hints: UnlockHint[];
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
    summary?: {
      data_tier?: DataTier | string;
      recommended_missing?: string[];
      [key: string]: unknown;
    };
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

/** Minimum billing export, any recognized billing CSV satisfies upload requirements. */
export const MINIMUM_BILLING_FILES: FileType[] = [
  "customers",
  "subscriptions",
  "invoices",
  "invoice_line_items",
  "coupons",
  "price_catalog",
];

/** @deprecated No hard-required files, use MINIMUM_BILLING_FILES. */
export const TIER_0_REQUIRED_FILES: FileType[] = MINIMUM_BILLING_FILES;

/** @deprecated Any billing entity satisfies minimum data requirements. */
export const TIER_0_REQUIRED_ENTITIES: CanonicalEntity[] = [
  "customer",
  "subscription",
  "invoice",
  "invoice_line_item",
  "price",
  "coupon",
];

/** Tier 1, strongly recommended for higher-confidence billing coverage. */
export const TIER_1_RECOMMENDED_FILES: FileType[] = [
  "subscriptions",
  "invoices",
  "customers",
  "price_catalog",
];

export const TIER_1_RECOMMENDED_ENTITIES: CanonicalEntity[] = [
  "subscription",
  "invoice",
  "customer",
  "price",
];

/** Tier 2, optional discount and credit enrichment. */
export const TIER_2_OPTIONAL_FILES: FileType[] = ["coupons"];

/** Tier 3, optional CRM power-ups. */
export const TIER_3_OPTIONAL_FILES: FileType[] = [
  "crm_accounts",
  "crm_opportunities",
  "crm_contracts",
];

/** @deprecated Use TIER_0_REQUIRED_FILES, kept for backward compatibility. */
export const REQUIRED_BILLING_FILES: FileType[] = TIER_0_REQUIRED_FILES;

export const ENTITY_LABELS: Record<CanonicalEntity, string> = {
  customer: "Customer",
  subscription: "Subscription",
  invoice: "Invoice",
  invoice_line_item: "Invoice Line Item",
  price: "Price",
  coupon: "Coupon",
  contract: "Contract",
  account: "Account",
  opportunity: "Opportunity",
};

export const FILE_TYPE_LABELS: Record<FileType, string> = {
  customers: "Customers",
  subscriptions: "Subscriptions",
  invoices: "Invoices",
  invoice_line_items: "Invoice Line Items",
  coupons: "Coupons",
  price_catalog: "Prices / Price Catalog",
  crm_accounts: "CRM Accounts",
  crm_opportunities: "CRM Opportunities",
  crm_contracts: "CRM Contracts",
  unknown: "Unknown",
};

export const FILE_TYPE_FILENAMES: Partial<Record<FileType, string[]>> = {
  customers: ["customers.csv"],
  subscriptions: ["subscriptions.csv"],
  invoices: ["invoices.csv"],
  invoice_line_items: ["invoice_line_items.csv"],
  coupons: ["coupons.csv"],
  price_catalog: ["price_catalog.csv", "prices.csv"],
  crm_accounts: ["accounts.csv", "crm_accounts.csv"],
  crm_opportunities: ["opportunities.csv", "crm_opportunities.csv"],
  crm_contracts: ["contracts.csv", "crm_contracts.csv"],
};

export const DATA_TIER_LABELS: Record<DataTier, string> = {
  insufficient: "Insufficient data",
  tier_0: "Tier 0, Core pricing",
  tier_1: "Tier 1, Full billing",
  tier_2_plus: "Tier 2+, Enriched",
};

export const PLATFORM_LABELS: Record<Platform, string> = {
  stripe: "Stripe",
  chargebee: "Chargebee",
  maxio: "Maxio",
  zuora: "Zuora",
  generic: "Generic",
};

export type FindingSeverity = "critical" | "high" | "medium" | "low";

export interface OpportunityBreakdownItem {
  category: string;
  label: string;
  arr: string;
  confidence: string | null;
  issue_count: number;
  account_count: number;
}

export interface VerificationCheckItem {
  rule_id: string;
  name: string;
  status: "passed" | "issues_found" | "partial" | "not_run" | "error";
  finding_count: number;
  arr: string;
  skip_reason?: string | null;
  coverage_note?: string | null;
}

export interface LockedPreviewItem {
  title: string;
  category: string;
  category_label: string;
  arr: string;
}

export interface SummaryCoverage {
  data_tier: string;
  billing_files_uploaded: string[];
  billing_files_missing: string[];
  crm_files_uploaded: string[];
  crm_present: boolean;
  confidence_impact: string;
}

export interface FreeSummaryResponse {
  audit_id: string;
  report_id: string;
  recoverable_arr: string;
  confidence: string | null;
  finding_count: number;
  accounts_reviewed: number;
  invoices_reviewed: number;
  rules_completed: number;
  rules_total: number;
  opportunity_breakdown: OpportunityBreakdownItem[];
  verification_checks: VerificationCheckItem[];
  locked_preview: LockedPreviewItem[];
  reconciliation?: ReconciliationSummary;
  coverage: SummaryCoverage;
  purchased: boolean;
  generated_at: string | null;
}

export interface ReconciliationSummary {
  total_findings: number;
  primary_findings: number;
  secondary_findings: number;
  primary_recoverable_arr: string;
  secondary_excluded_arr: string;
  raw_sum_arr: string;
  headline_recoverable_arr: string;
}

export interface LeakageComputation {
  semantics: "recurring_run_rate" | "per_period" | "one_time";
  unit_expected: string;
  unit_actual: string;
  quantity: number;
  billing_interval: string;
  monthly_loss: string;
  annual_loss: string;
  formula: string;
}

export interface EvidenceRecord {
  field: string;
  expected?: string | null;
  actual?: string | null;
  reference_ids?: Record<string, string>;
}

export interface CalculationStep {
  step_id: string;
  label: string;
  value: string;
  unit?: string | null;
  source_refs?: Record<string, string>;
}

export interface CalculationTrace {
  steps: CalculationStep[];
  result_monthly: string;
  result_annual: string;
  semantics: string;
}

export interface FindingResponse {
  id: string;
  rule_id: string;
  title: string;
  category: string;
  category_label: string;
  severity: FindingSeverity | string;
  confidence: string;
  customer_id: string | null;
  subscription_id: string | null;
  invoice_id: string | null;
  estimated_monthly_loss: string;
  estimated_arr_loss: string;
  recommendation: string | null;
  attribution?: "primary" | "secondary";
  leak_family?: string | null;
  finding_ref?: string | null;
  primary_finding_ref?: string | null;
  primary_finding_id?: string | null;
  primary_finding_title?: string | null;
  recoverable_amount?: string;
  leakage_semantics?: string | null;
  leakage_computation?: LeakageComputation;
  calculation_trace?: CalculationTrace;
  evidence: Record<string, unknown>;
  evidence_records: EvidenceRecord[];
}

export interface ExecutiveSummary {
  recoverable_arr: string;
  high_confidence_arr: string;
  medium_confidence_arr: string;
  low_confidence_arr: string;
  accounts_reviewed: number;
  invoices_reviewed: number;
  finding_count: number;
  confidence: string | null;
  rules_completed: number;
  rules_total: number;
  narrative: string;
  reconciliation?: ReconciliationSummary;
}

export interface ReportDetailResponse {
  id: string;
  audit_id: string;
  purchased: boolean;
  generated_at: string | null;
  company_name: string | null;
  executive_summary: ExecutiveSummary;
  opportunity_breakdown: OpportunityBreakdownItem[];
  verification_checks: VerificationCheckItem[];
  findings: FindingResponse[];
}

export interface FindingDetailResponse extends FindingResponse {
  audit_id: string;
  report_id: string;
}

export interface ReportListItem {
  audit_id: string;
  report_id: string;
  date: string | null;
  recoverable_arr: string;
  status: AuditStatus;
  finding_count: number;
  purchased: boolean;
  company_name: string | null;
}

export interface DashboardResponse {
  company_name: string | null;
  reports_remaining: number;
  audits: ReportListItem[];
}

export interface UnlockReportResponse {
  report_id: string;
  purchased: boolean;
  message: string;
}

export type CheckoutPlan = "single_report" | "annual_membership";

export interface CheckoutRequest {
  plan: CheckoutPlan;
  report_id?: string | null;
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface CheckoutStatusResponse {
  session_id: string;
  payment_status: string;
  report_id: string | null;
  plan: string | null;
  fulfilled: boolean;
  reports_remaining: number;
}

export interface PurchaseRecord {
  report_id: string | null;
  plan: string;
  amount_cents: number | null;
  currency: string | null;
  receipt_url: string | null;
  created_at: string | null;
}

export interface BillingResponse {
  plan: string;
  status: string;
  reports_remaining: number;
  portal_url: string | null;
  purchases: PurchaseRecord[];
}

export interface UnlockCreditResponse {
  report_id: string;
  purchased: boolean;
  reports_remaining: number;
  message: string;
}

export function formatDecimal(
  value: string | number | null | undefined,
  maxFractionDigits = 2,
): string {
  if (value === null || value === undefined) return "-";
  const raw = String(value).trim();
  if (!raw || raw === "-") return raw || "-";

  if (raw.includes("→")) {
    return raw
      .split("→")
      .map((part) => formatDecimal(part.trim(), maxFractionDigits))
      .join(" → ");
  }

  const normalized = raw.replace(/[$,%]/g, "").replace(/,/g, "");
  const amount = typeof value === "number" ? value : parseFloat(normalized);
  if (Number.isNaN(amount)) return raw;

  return new Intl.NumberFormat("en-US", {
    minimumFractionDigits: 0,
    maximumFractionDigits: maxFractionDigits,
    useGrouping: false,
  }).format(amount);
}

export function formatCurrency(value: string | number): string {
  const amount = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(amount)) return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(amount);
}

export function isTier0Complete(uploadedTypes: FileType[]): boolean {
  return uploadedTypes.some((type) => MINIMUM_BILLING_FILES.includes(type));
}

export function hasBillingUpload(uploadedTypes: FileType[]): boolean {
  return isTier0Complete(uploadedTypes);
}

export function isTier0EntitiesComplete(entities: CanonicalEntity[]): boolean {
  return TIER_0_REQUIRED_ENTITIES.some((entity) => entities.includes(entity));
}

export {
  AnalyticsEvents,
  type AnalyticsCommonProperties,
  type AnalyticsEventName,
  type AnalyticsEventProperties,
  type AuditAnalyticsProperties,
  type AuditType,
  type CheckoutType,
} from "./analytics";
