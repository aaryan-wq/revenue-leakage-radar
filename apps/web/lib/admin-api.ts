import type {
  AdminAuditDetailResponse,
  AdminMeResponse,
  AdminOverviewResponse,
  AdminReprocessResponse,
  AdminRefundResponse,
  PaginatedAuditsResponse,
  PaginatedCompaniesResponse,
  PaginatedLogsResponse,
  PaginatedAssessmentsResponse,
  PaginatedReportsResponse,
  PaginatedSupportNotesResponse,
  SupportNote,
  SupportNoteCreateRequest,
} from "@rlr/shared";

import { apiFetch } from "./api";

function authOptions(authToken: string) {
  return { authToken };
}

export async function getAdminMe(authToken: string): Promise<AdminMeResponse> {
  return apiFetch<AdminMeResponse>("/admin/me", authOptions(authToken));
}

export async function getAdminOverview(authToken: string): Promise<AdminOverviewResponse> {
  return apiFetch<AdminOverviewResponse>("/admin/overview", authOptions(authToken));
}

export async function getAdminCompanies(
  authToken: string,
  params: { q?: string; page?: number; page_size?: number } = {},
): Promise<PaginatedCompaniesResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiFetch<PaginatedCompaniesResponse>(
    `/admin/companies${query ? `?${query}` : ""}`,
    authOptions(authToken),
  );
}

export async function getAdminAudits(
  authToken: string,
  params: { q?: string; page?: number; page_size?: number } = {},
): Promise<PaginatedAuditsResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiFetch<PaginatedAuditsResponse>(
    `/admin/audits${query ? `?${query}` : ""}`,
    authOptions(authToken),
  );
}

export async function getAdminAuditDetail(
  authToken: string,
  auditId: string,
): Promise<AdminAuditDetailResponse> {
  return apiFetch<AdminAuditDetailResponse>(`/admin/audits/${auditId}`, authOptions(authToken));
}

export async function getAdminReports(
  authToken: string,
  params: { q?: string; purchased?: boolean; page?: number; page_size?: number } = {},
): Promise<PaginatedReportsResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.purchased !== undefined) search.set("purchased", String(params.purchased));
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiFetch<PaginatedReportsResponse>(
    `/admin/reports${query ? `?${query}` : ""}`,
    authOptions(authToken),
  );
}

export async function getAdminAssessments(
  authToken: string,
  params: { q?: string; status?: string; page?: number; page_size?: number } = {},
): Promise<PaginatedAssessmentsResponse> {
  const search = new URLSearchParams();
  if (params.q) search.set("q", params.q);
  if (params.status) search.set("status", params.status);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiFetch<PaginatedAssessmentsResponse>(
    `/admin/assessments${query ? `?${query}` : ""}`,
    authOptions(authToken),
  );
}

export async function getAdminLogs(
  authToken: string,
  params: {
    entity_type?: string;
    entity_id?: string;
    page?: number;
    page_size?: number;
  } = {},
): Promise<PaginatedLogsResponse> {
  const search = new URLSearchParams();
  if (params.entity_type) search.set("entity_type", params.entity_type);
  if (params.entity_id) search.set("entity_id", params.entity_id);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiFetch<PaginatedLogsResponse>(
    `/admin/logs${query ? `?${query}` : ""}`,
    authOptions(authToken),
  );
}

export async function getAdminSupportNotes(
  authToken: string,
  params: {
    entity_type?: string;
    entity_id?: string;
    page?: number;
    page_size?: number;
  } = {},
): Promise<PaginatedSupportNotesResponse> {
  const search = new URLSearchParams();
  if (params.entity_type) search.set("entity_type", params.entity_type);
  if (params.entity_id) search.set("entity_id", params.entity_id);
  if (params.page) search.set("page", String(params.page));
  if (params.page_size) search.set("page_size", String(params.page_size));
  const query = search.toString();
  return apiFetch<PaginatedSupportNotesResponse>(
    `/admin/support-notes${query ? `?${query}` : ""}`,
    authOptions(authToken),
  );
}

export async function createAdminSupportNote(
  authToken: string,
  body: SupportNoteCreateRequest,
): Promise<SupportNote> {
  return apiFetch<SupportNote>("/admin/support-notes", {
    ...authOptions(authToken),
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

export async function adminReprocessAudit(
  authToken: string,
  auditId: string,
): Promise<AdminReprocessResponse> {
  return apiFetch<AdminReprocessResponse>("/admin/reprocess", {
    ...authOptions(authToken),
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ audit_id: auditId }),
  });
}

export async function adminDeleteReport(authToken: string, reportId: string): Promise<void> {
  await apiFetch<void>(`/admin/reports/${reportId}`, {
    ...authOptions(authToken),
    method: "DELETE",
  });
}

export async function adminUnlockReport(
  authToken: string,
  reportId: string,
): Promise<{ report_id: string; purchased: boolean }> {
  return apiFetch<{ report_id: string; purchased: boolean }>(`/admin/reports/${reportId}/unlock`, {
    ...authOptions(authToken),
    method: "POST",
  });
}

export async function adminDeleteUpload(authToken: string, uploadId: string): Promise<void> {
  await apiFetch<void>(`/admin/uploads/${uploadId}`, {
    ...authOptions(authToken),
    method: "DELETE",
  });
}

export async function adminRefundPurchase(
  authToken: string,
  purchaseId: string,
  reason?: string,
): Promise<AdminRefundResponse> {
  return apiFetch<AdminRefundResponse>("/admin/refunds", {
    ...authOptions(authToken),
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ purchase_id: purchaseId, reason }),
  });
}
