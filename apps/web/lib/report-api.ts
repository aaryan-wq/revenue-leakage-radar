import type {
  BillingResponse,
  CheckoutPlan,
  CheckoutRequest,
  CheckoutResponse,
  CheckoutStatusResponse,
  DashboardResponse,
  FindingDetailResponse,
  FreeSummaryResponse,
  PaginatedFindingsResponse,
  ReportDetailResponse,
  UnlockCreditResponse,
  UnlockReportResponse,
} from "@rlr/shared";

import { apiDownload, apiFetch } from "./api";
import type { AuditSession } from "./audit-session";

export interface ReportApiOptions {
  auditSession?: string;
  authToken?: string | null;
}

function withSession(session: AuditSession | null, authToken?: string | null): ReportApiOptions {
  return {
    auditSession: session?.sessionToken,
    authToken,
  };
}

export async function getSummary(
  auditId: string,
  session: AuditSession,
  authToken?: string | null,
): Promise<FreeSummaryResponse> {
  return apiFetch<FreeSummaryResponse>(`/summary/${auditId}`, {
    auditSession: session.sessionToken,
    authToken,
  });
}

export async function getReport(
  reportId: string,
  options: ReportApiOptions,
): Promise<ReportDetailResponse> {
  return apiFetch<ReportDetailResponse>(`/reports/${reportId}`, options);
}

export interface ReportFindingsQuery {
  page?: number;
  page_size?: number;
  sort?: "arr_desc" | "severity" | "rule_id";
  category?: string;
}

export async function getReportFindings(
  reportId: string,
  options: ReportApiOptions,
  query: ReportFindingsQuery = {},
): Promise<PaginatedFindingsResponse> {
  const params = new URLSearchParams();
  if (query.page) params.set("page", String(query.page));
  if (query.page_size) params.set("page_size", String(query.page_size));
  if (query.sort) params.set("sort", query.sort);
  if (query.category) params.set("category", query.category);
  const suffix = params.toString() ? `?${params.toString()}` : "";
  return apiFetch<PaginatedFindingsResponse>(`/reports/${reportId}/findings${suffix}`, options);
}

export async function getFinding(
  findingId: string,
  options: ReportApiOptions,
): Promise<FindingDetailResponse> {
  return apiFetch<FindingDetailResponse>(`/findings/${findingId}`, options);
}

export async function getDashboard(authToken: string): Promise<DashboardResponse> {
  return apiFetch<DashboardResponse>("/dashboard", { authToken });
}

export async function devUnlockReport(reportId: string): Promise<UnlockReportResponse> {
  return apiFetch<UnlockReportResponse>(`/dev/reports/${reportId}/unlock`, {
    method: "POST",
  });
}

export async function createCheckout(
  plan: CheckoutPlan,
  authToken: string,
  reportId?: string | null,
  auditSession?: string | null,
): Promise<CheckoutResponse> {
  const body: CheckoutRequest = { plan };
  if (reportId) {
    body.report_id = reportId;
  }
  return apiFetch<CheckoutResponse>("/checkout", {
    method: "POST",
    authToken,
    auditSession: auditSession ?? undefined,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function getCheckoutStatus(
  sessionId: string,
  authToken: string,
): Promise<CheckoutStatusResponse> {
  return apiFetch<CheckoutStatusResponse>(
    `/checkout/status?session_id=${encodeURIComponent(sessionId)}`,
    { authToken },
  );
}

export async function getBilling(authToken: string): Promise<BillingResponse> {
  return apiFetch<BillingResponse>("/billing", { authToken });
}

export async function deleteAudit(auditId: string, authToken: string): Promise<void> {
  await apiFetch<void>(`/audit/${auditId}`, {
    method: "DELETE",
    authToken,
  });
}

export async function unlockWithCredit(
  reportId: string,
  authToken: string,
  auditSession?: string | null,
): Promise<UnlockCreditResponse> {
  return apiFetch<UnlockCreditResponse>(`/reports/${reportId}/unlock-credit`, {
    method: "POST",
    authToken,
    auditSession: auditSession ?? undefined,
  });
}

export async function downloadPdf(reportId: string, options: ReportApiOptions): Promise<Blob> {
  return apiDownload(`/exports/pdf/${reportId}`, { ...options, timeoutMs: 120_000 });
}

export async function downloadCsv(reportId: string, options: ReportApiOptions): Promise<Blob> {
  return apiDownload(`/exports/csv/${reportId}`, { ...options, timeoutMs: 60_000 });
}

export async function downloadEvidenceCsv(reportId: string, options: ReportApiOptions): Promise<Blob> {
  return apiDownload(`/exports/evidence/${reportId}`, { ...options, timeoutMs: 60_000 });
}

export function triggerBlobDownload(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(url);
}

export async function downloadReportPdf(
  reportId: string,
  session: AuditSession | null,
  authToken?: string | null,
): Promise<void> {
  const blob = await downloadPdf(reportId, withSession(session, authToken));
  triggerBlobDownload(blob, `revenue-report-${reportId}.pdf`);
}

export async function downloadReportCsv(
  reportId: string,
  session: AuditSession | null,
  authToken?: string | null,
): Promise<void> {
  const blob = await downloadCsv(reportId, withSession(session, authToken));
  triggerBlobDownload(blob, `revenue-findings-${reportId}.csv`);
}

export async function downloadReportEvidenceCsv(
  reportId: string,
  session: AuditSession | null,
  authToken?: string | null,
): Promise<void> {
  const blob = await downloadEvidenceCsv(reportId, withSession(session, authToken));
  triggerBlobDownload(blob, `revenue-evidence-${reportId}.csv`);
}
