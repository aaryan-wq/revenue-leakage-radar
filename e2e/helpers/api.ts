import type { APIRequestContext } from "@playwright/test";

import { apiBaseUrl } from "./env";

export async function devUnlockReport(
  request: APIRequestContext,
  reportId: string,
): Promise<void> {
  const response = await request.post(`${apiBaseUrl()}/dev/reports/${reportId}/unlock`);
  if (!response.ok()) {
    const body = await response.text();
    throw new Error(`Dev unlock failed (${response.status}): ${body}`);
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
