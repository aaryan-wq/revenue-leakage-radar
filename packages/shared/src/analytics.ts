/** Canonical product analytics event names, keep in sync with apps/api/analytics/events.py */

export const AnalyticsEvents = {
  // Public website / marketing
  LANDING_PAGE_VIEWED: "landing_page_viewed",
  PRICING_PAGE_VIEWED: "pricing_page_viewed",
  SECURITY_PAGE_VIEWED: "security_page_viewed",
  FAQ_PAGE_VIEWED: "faq_page_viewed",
  FREE_AUDIT_CTA_CLICKED: "free_audit_cta_clicked",
  PRICING_CTA_CLICKED: "pricing_cta_clicked",
  ENTERPRISE_CTA_CLICKED: "enterprise_cta_clicked",
  CONTACT_SALES_CLICKED: "contact_sales_clicked",
  CONTACT_SALES_SUBMITTED: "contact_sales_submitted",
  FEEDBACK_FAB_CLICKED: "feedback_fab_clicked",
  FEEDBACK_FORM_OPENED: "feedback_form_opened",
  FEEDBACK_SUBMITTED: "feedback_submitted",
  FEEDBACK_PAGE_VIEWED: "feedback_page_viewed",

  // Audit lifecycle
  AUDIT_SESSION_CREATED: "audit_session_created",
  AUDIT_STARTED: "audit_started",
  AUDIT_CANCELLED: "audit_cancelled",
  AUDIT_COMPLETED: "audit_completed",
  AUDIT_FAILED: "audit_failed",

  // Upload + validation
  CSV_UPLOAD_STARTED: "csv_upload_started",
  CSV_UPLOAD_COMPLETED: "csv_upload_completed",
  CSV_UPLOAD_FAILED: "csv_upload_failed",
  CSV_REMOVED: "csv_removed",
  CSV_REPLACED: "csv_replaced",
  CSV_VALIDATION_STARTED: "csv_validation_started",
  CSV_VALIDATION_COMPLETED: "csv_validation_completed",
  CSV_VALIDATION_FAILED: "csv_validation_failed",
  CSV_MAPPING_REVIEWED: "csv_mapping_reviewed",
  CSV_MAPPING_CORRECTED: "csv_mapping_corrected",

  // Verification
  VERIFICATION_STARTED: "verification_started",
  VERIFICATION_COMPLETED: "verification_completed",
  VERIFICATION_FAILED: "verification_failed",
  RULE_EXECUTED: "rule_executed",
  RULE_SKIPPED: "rule_skipped",
  RULE_FAILED: "rule_failed",
  FINDING_CREATED: "finding_created",
  FINDING_SUPPRESSED: "finding_suppressed",
  COVERAGE_SCORE_CALCULATED: "coverage_score_calculated",

  // Free summary
  FREE_SUMMARY_VIEWED: "free_summary_viewed",
  FREE_SUMMARY_REFRESHED: "free_summary_refreshed",
  FINDING_PREVIEW_EXPANDED: "finding_preview_expanded",
  REPORT_UNLOCK_CTA_CLICKED: "report_unlock_cta_clicked",
  CONTACT_SALES_FROM_RESULTS_CLICKED: "contact_sales_from_results_clicked",

  // Checkout / monetization
  CHECKOUT_STARTED: "checkout_started",
  CHECKOUT_COMPLETED: "checkout_completed",
  CHECKOUT_FAILED: "checkout_failed",
  REPORT_ACCESS_UNLOCKED: "report_access_unlocked",
  CONTACT_SALES_FROM_PRICING_CLICKED: "contact_sales_from_pricing_clicked",

  // Paid report consumption
  PAID_REPORT_VIEWED: "paid_report_viewed",
  FINDING_DETAIL_VIEWED: "finding_detail_viewed",
  REPORT_EXPORTED_PDF: "report_exported_pdf",
  REPORT_EXPORTED_CSV: "report_exported_csv",
  REMEDIATION_VIEWED: "remediation_viewed",
} as const;

export type AnalyticsEventName = (typeof AnalyticsEvents)[keyof typeof AnalyticsEvents];

export type AuditType = "free" | "paid" | "enterprise";

export type CheckoutType = "single_report" | "enterprise" | "credit_unlock";

export interface AnalyticsCommonProperties {
  session_id?: string;
  anonymous_user_id?: string;
  user_id?: string;
  page_path?: string;
  referrer?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  device_type?: "desktop" | "tablet" | "mobile";
}

export interface AuditAnalyticsProperties {
  audit_id?: string;
  audit_type?: AuditType;
  is_anonymous?: boolean;
  billing_platform_detected?: string | null;
  crm_platform_detected?: string | null;
  csv_file_count?: number;
  billing_file_count?: number;
  crm_file_count?: number;
}

export type AnalyticsEventProperties = AnalyticsCommonProperties &
  AuditAnalyticsProperties &
  Record<string, string | number | boolean | null | undefined>;
