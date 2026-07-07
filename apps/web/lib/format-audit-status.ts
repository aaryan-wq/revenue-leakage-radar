import type { AuditStatus } from "@rlr/shared";

const STATUS_LABELS: Partial<Record<AuditStatus, string>> = {
  completed: "Complete",
  scanning: "Scanning",
  generating_report: "Generating report",
  ready_for_scan: "Ready to scan",
  normalizing: "Normalizing",
  validating: "Validating",
  mapping: "Mapping",
  uploading: "Uploading",
  validation_failed: "Validation failed",
  processing_failed: "Processing failed",
  upload_failed: "Upload failed",
  payment_pending: "Payment pending",
  created: "Created",
};

export function formatAuditStatusLabel(status: string): string {
  const mapped = STATUS_LABELS[status as AuditStatus];
  if (mapped) return mapped;
  return status.replace(/_/g, " ");
}
