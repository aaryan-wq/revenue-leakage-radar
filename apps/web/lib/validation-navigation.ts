import type { ValidationReportResponse } from "@rlr/shared";

export function canNavigateToAnalysis(report: ValidationReportResponse): boolean {
  if (report.can_proceed_to_scan) return true;
  if (report.status === "completed") return true;
  if (report.status === "scanning" || report.status === "generating_report") return true;
  return false;
}

export function analysisNavigationLabel(report: ValidationReportResponse): string {
  if (report.status === "completed") return "View Results";
  if (report.status === "scanning" || report.status === "generating_report") {
    return "Resume Analysis";
  }
  if (report.status === "processing_failed") return "Retry Scan";
  return "Continue to Analysis";
}
