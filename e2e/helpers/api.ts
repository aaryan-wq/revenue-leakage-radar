import type { APIRequestContext, Page } from "@playwright/test";
import { clerk } from "@clerk/testing/playwright";

import { apiBaseUrl } from "./env";

export interface ApiAuthOptions {
  sessionToken?: string | null;
  authToken?: string | null;
}

function buildAuthHeaders(options: ApiAuthOptions = {}): Record<string, string> {
  const headers: Record<string, string> = {};
  if (options.sessionToken) {
    headers["X-Audit-Session"] = options.sessionToken;
  }
  if (options.authToken) {
    headers.Authorization = `Bearer ${options.authToken}`;
  }
  return headers;
}

export async function getClerkAuthToken(page: Page): Promise<string | null> {
  await clerk.loaded({ page });
  return page.evaluate(async () => {
    const clerkClient = (window as Window & { Clerk?: { session?: { getToken: () => Promise<string | null> } } })
      .Clerk;
    return clerkClient?.session?.getToken() ?? null;
  });
}

export async function linkAuditToClerkUser(
  request: APIRequestContext,
  auditId: string,
  authToken: string,
  sessionToken?: string,
): Promise<void> {
  const response = await request.post(`${apiBaseUrl()}/audit/${auditId}/link`, {
    headers: buildAuthHeaders({ authToken, sessionToken }),
  });
  if (!response.ok() && response.status() !== 204) {
    const body = await response.text();
    throw new Error(`Audit link failed (${response.status()}): ${body}`);
  }
}

export async function devUnlockReport(
  request: APIRequestContext,
  reportId: string,
  authToken?: string,
): Promise<void> {
  const response = await request.post(`${apiBaseUrl()}/dev/reports/${reportId}/unlock`, {
    headers: buildAuthHeaders({ authToken }),
  });
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Dev unlock failed (${response.status()}): ${body}`);
  }
}

export async function getSummaryForAudit(
  request: APIRequestContext,
  auditId: string,
  auth: ApiAuthOptions = {},
): Promise<{ report_id?: string; recoverable_arr?: string; finding_count?: number }> {
  const response = await request.get(`${apiBaseUrl()}/summary/${auditId}`, {
    headers: buildAuthHeaders(auth),
  });
  if (!response.ok()) {
    throw new Error(`Summary fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getReportDetail(
  request: APIRequestContext,
  reportId: string,
  auth: ApiAuthOptions = {},
): Promise<{ findings_total?: number; findings?: Array<{ id: string }> }> {
  const response = await request.get(`${apiBaseUrl()}/reports/${reportId}`, {
    headers: buildAuthHeaders(auth),
  });
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Report fetch failed (${response.status}): ${body}`);
  }
  return response.json();
}

export async function getReportFindings(
  request: APIRequestContext,
  reportId: string,
  auth: ApiAuthOptions = {},
  query: { page?: number; page_size?: number } = {},
): Promise<{ items: Array<{ id: string }>; total: number; has_more: boolean }> {
  const params = new URLSearchParams();
  if (query.page) params.set("page", String(query.page));
  if (query.page_size) params.set("page_size", String(query.page_size));
  const suffix = params.toString() ? `?${params.toString()}` : "";

  const response = await request.get(`${apiBaseUrl()}/reports/${reportId}/findings${suffix}`, {
    headers: buildAuthHeaders(auth),
  });
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Report findings fetch failed (${response.status}): ${body}`);
  }
  return response.json();
}

export async function getFindingDetail(
  request: APIRequestContext,
  findingId: string,
  auth: ApiAuthOptions = {},
): Promise<Record<string, unknown>> {
  const response = await request.get(`${apiBaseUrl()}/findings/${findingId}`, {
    headers: buildAuthHeaders(auth),
  });
  if (!response.ok()) {
    throw new Error(`Finding fetch failed (${response.status})`);
  }
  return response.json();
}
