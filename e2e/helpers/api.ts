import type { APIRequestContext, Page } from "@playwright/test";
import { clerk } from "@clerk/testing/playwright";

import { apiBaseUrl } from "./env";

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
  const headers: Record<string, string> = { Authorization: `Bearer ${authToken}` };
  if (sessionToken) {
    headers["X-Audit-Session"] = sessionToken;
  }

  const response = await request.post(`${apiBaseUrl()}/audit/${auditId}/link`, { headers });
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
  const headers: Record<string, string> = {};
  if (authToken) {
    headers.Authorization = `Bearer ${authToken}`;
  }

  const response = await request.post(`${apiBaseUrl()}/dev/reports/${reportId}/unlock`, { headers });
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Dev unlock failed (${response.status()}): ${body}`);
  }
}

export async function getSummaryForAudit(
  request: APIRequestContext,
  auditId: string,
  sessionToken: string,
): Promise<{ report_id?: string; recoverable_arr?: string }> {
  const response = await request.get(`${apiBaseUrl()}/summary/${auditId}`, {
    headers: { "X-Audit-Session": sessionToken },
  });
  if (!response.ok()) {
    throw new Error(`Summary fetch failed (${response.status})`);
  }
  return response.json();
}

export async function getReportDetail(
  request: APIRequestContext,
  reportId: string,
  sessionToken: string,
): Promise<{ findings: Array<{ id: string }> }> {
  const response = await request.get(`${apiBaseUrl()}/reports/${reportId}`, {
    headers: { "X-Audit-Session": sessionToken },
  });
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Report fetch failed (${response.status}): ${body}`);
  }
  return response.json();
}

export async function getFindingDetail(
  request: APIRequestContext,
  findingId: string,
  sessionToken?: string,
  authToken?: string,
): Promise<Record<string, unknown>> {
  const headers: Record<string, string> = {};
  if (sessionToken) headers["X-Audit-Session"] = sessionToken;
  if (authToken) headers.Authorization = `Bearer ${authToken}`;

  const response = await request.get(`${apiBaseUrl()}/findings/${findingId}`, { headers });
  if (!response.ok()) {
    throw new Error(`Finding fetch failed (${response.status})`);
  }
  return response.json();
}
