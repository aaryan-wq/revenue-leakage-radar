import type {
  AuditCreateResponse,
  AuditStatus,
  AuditStatusResponse,
  ScanReportResponse,
  ScanResponse,
  UploadResponse,
  ValidateResponse,
  ValidationReportResponse,
} from "@rlr/shared";
import { PROCESSING_STATUSES, SCAN_PROCESSING_STATUSES } from "@rlr/shared";

import { apiFetch, ApiError } from "./api";
import { API_URL } from "./api-url";

type AuthTokenProvider = () => Promise<string | null>;

let authTokenProvider: AuthTokenProvider | null = null;

/** Registers Clerk token lookup for audit funnel API calls (required after account link). */
export function setAuditAuthTokenProvider(provider: AuthTokenProvider | null): void {
  authTokenProvider = provider;
}

async function resolveAuthToken(explicit?: string | null): Promise<string | null | undefined> {
  if (explicit !== undefined) return explicit;
  if (!authTokenProvider) return undefined;
  return authTokenProvider();
}

export async function getAuditAuthToken(): Promise<string | null> {
  const token = await resolveAuthToken();
  return token ?? null;
}

async function auditApiFetch<T>(
  path: string,
  options: Parameters<typeof apiFetch>[1] = {},
): Promise<T> {
  const authToken = await resolveAuthToken(options.authToken);
  return apiFetch<T>(path, { ...options, authToken });
}

const SESSION_KEY = "rlr_audit_session";
const AUDIT_ID_KEY = "rlr_audit_id";
const AUDIT_ORIGIN_KEY = "rlr_audit_origin";

export type AuditOrigin = "workspace" | "public";

export const WORKSPACE_UPLOAD_HREF = "/upload?from=workspace";
export const WORKSPACE_EXIT_HREF = "/dashboard";

export interface AuditSession {
  auditId: string;
  sessionToken: string;
}

export function getStoredAuditSession(): AuditSession | null {
  if (typeof window === "undefined") return null;

  const auditId = localStorage.getItem(AUDIT_ID_KEY);
  const sessionToken = localStorage.getItem(SESSION_KEY);

  if (!auditId || !sessionToken) return null;
  return { auditId, sessionToken };
}

export function storeAuditSession(session: AuditSession): void {
  localStorage.setItem(AUDIT_ID_KEY, session.auditId);
  localStorage.setItem(SESSION_KEY, session.sessionToken);
}

export function clearAuditSession(): void {
  localStorage.removeItem(AUDIT_ID_KEY);
  localStorage.removeItem(SESSION_KEY);
  localStorage.removeItem(AUDIT_ORIGIN_KEY);
}

/** Discard in-progress server data and clear the browser audit session. */
export async function linkAuditToAccount(
  session: AuditSession,
  authToken: string,
): Promise<void> {
  await auditApiFetch<void>(`/audit/${session.auditId}/link`, {
    method: "POST",
    auditSession: session.sessionToken,
    authToken,
  });
}

/** Link a completed audit using Clerk auth (works when already linked; unlinked audits still need a session). */
export async function linkAuditById(auditId: string, authToken: string): Promise<void> {
  await auditApiFetch<void>(`/audit/${auditId}/link`, {
    method: "POST",
    authToken,
  });
}

/** Attach the in-progress audit to the signed-in Clerk account so it appears in the workspace. */
export async function ensureAuditLinked(authToken: string): Promise<boolean> {
  const session = getStoredAuditSession();
  if (!session) return false;

  try {
    await linkAuditToAccount(session, authToken);
    return true;
  } catch {
    return false;
  }
}

export function isCompletedAuditPath(pathname: string): boolean {
  return pathname === "/summary" || pathname.startsWith("/summary/");
}

export interface SaveCompletedAuditOptions {
  /** Fallback when local session was cleared after an earlier link attempt. */
  auditId?: string;
}

/** Save a completed audit to the signed-in account and clear the browser session. */
export async function saveCompletedAuditOnExit(
  authToken?: string | null,
  options?: SaveCompletedAuditOptions,
): Promise<void> {
  const token = authToken ?? (await getAuditAuthToken());
  if (!token) {
    throw new Error("Sign in to save this audit to your workspace.");
  }

  const session = getStoredAuditSession();
  const auditId = options?.auditId ?? session?.auditId;
  if (!auditId) {
    throw new Error("Audit session expired. Return to your summary and try again.");
  }

  if (session) {
    try {
      await linkAuditToAccount(session, token);
    } catch (err) {
      // Session token may be stale after a prior link; auth-only retry still succeeds for owned audits.
      if (err instanceof ApiError && err.status === 404) {
        await linkAuditById(auditId, token);
      } else {
        throw err;
      }
    }
  } else {
    await linkAuditById(auditId, token);
  }

  clearAuditSession();
}

/** Leave the audit funnel: preserve completed audits, discard in-progress ones. */
export async function exitAuditFromFunnel(pathname: string): Promise<void> {
  if (isCompletedAuditPath(pathname)) {
    await saveCompletedAuditOnExit();
    return;
  }
  await abandonAuditOnExit();
}

export async function abandonAuditOnExit(): Promise<void> {
  const session = getStoredAuditSession();
  if (!session) return;

  try {
    await auditApiFetch<void>(`/audit/${session.auditId}/session`, {
      method: "DELETE",
      auditSession: session.sessionToken,
    });
  } catch {
    // Best effort. Never block navigation away from the audit funnel.
  } finally {
    clearAuditSession();
  }
}

export function setAuditOrigin(origin: AuditOrigin): void {
  localStorage.setItem(AUDIT_ORIGIN_KEY, origin);
}

export function getAuditOrigin(): AuditOrigin | null {
  if (typeof window === "undefined") return null;
  const value = localStorage.getItem(AUDIT_ORIGIN_KEY);
  if (value === "workspace" || value === "public") return value;
  return null;
}

export function getAuditExitHrefFromSearch(search: string | URLSearchParams): string {
  const params = typeof search === "string" ? new URLSearchParams(search) : search;
  return params.get("from") === "workspace" ? WORKSPACE_EXIT_HREF : "/";
}

export function getAuditExitHref(): string {
  if (typeof window !== "undefined") {
    const fromSearch = getAuditExitHrefFromSearch(window.location.search);
    if (fromSearch === WORKSPACE_EXIT_HREF) {
      return WORKSPACE_EXIT_HREF;
    }
  }
  return getAuditOrigin() === "workspace" ? WORKSPACE_EXIT_HREF : "/";
}

export function captureAuditOriginFromSearch(search: string | URLSearchParams): void {
  const params =
    typeof search === "string" ? new URLSearchParams(search) : search;
  if (params.get("from") === "workspace") {
    setAuditOrigin("workspace");
  }
}

export async function createAuditSession(): Promise<AuditSession> {
  const response = await auditApiFetch<AuditCreateResponse>("/audit", {
    method: "POST",
  });

  const session: AuditSession = {
    auditId: response.audit_id,
    sessionToken: response.session_token,
  };

  storeAuditSession(session);
  return session;
}

export async function getAuditStatus(session: AuditSession): Promise<AuditStatusResponse> {
  return auditApiFetch<AuditStatusResponse>(`/audit/${session.auditId}`, {
    auditSession: session.sessionToken,
  });
}

export async function startValidation(session: AuditSession): Promise<ValidateResponse> {
  return auditApiFetch<ValidateResponse>(`/audit/${session.auditId}/validate`, {
    method: "POST",
    auditSession: session.sessionToken,
  });
}

export async function getValidationReport(
  session: AuditSession,
): Promise<ValidationReportResponse> {
  return auditApiFetch<ValidationReportResponse>(`/audit/${session.auditId}/validation`, {
    auditSession: session.sessionToken,
  });
}

export function isProcessingStatus(status: AuditStatus): boolean {
  return PROCESSING_STATUSES.includes(status);
}

export function isScanProcessingStatus(status: AuditStatus): boolean {
  return SCAN_PROCESSING_STATUSES.includes(status);
}

/** True while a scan is actively running (used for analysis-page polling). */
export function isScanPollInProgress(status: AuditStatus): boolean {
  return isScanProcessingStatus(status);
}

export async function startScan(session: AuditSession): Promise<ScanResponse> {
  return auditApiFetch<ScanResponse>(`/audit/${session.auditId}/scan`, {
    method: "POST",
    auditSession: session.sessionToken,
  });
}

export async function getScanReport(session: AuditSession): Promise<ScanReportResponse> {
  return auditApiFetch<ScanReportResponse>(`/audit/${session.auditId}/scan`, {
    auditSession: session.sessionToken,
  });
}

export async function pollScanUntil(
  session: AuditSession,
  shouldContinue: (report: ScanReportResponse) => boolean,
  onTick?: (report: ScanReportResponse) => void,
  options?: { intervalMs?: number; maxAttempts?: number },
): Promise<ScanReportResponse> {
  const intervalMs = options?.intervalMs ?? 2000;
  const maxAttempts = options?.maxAttempts;

  return new Promise((resolve, reject) => {
    let attempts = 0;

    const poll = async () => {
      try {
        attempts += 1;
        const report = await getScanReport(session);
        onTick?.(report);
        if (!shouldContinue(report)) {
          resolve(report);
          return;
        }
        if (maxAttempts !== undefined && attempts >= maxAttempts) {
          reject(
            new ApiError(
              `Verification scan did not finish (last status: ${report.status}). Try Retry Scan.`,
              408,
            ),
          );
          return;
        }
        setTimeout(() => void poll(), intervalMs);
      } catch (err) {
        reject(err);
      }
    };
    void poll();
  });
}

export async function pollAuditUntil(
  session: AuditSession,
  shouldContinue: (status: AuditStatusResponse) => boolean,
  onTick?: (status: AuditStatusResponse) => void,
  intervalMs = 2000,
): Promise<AuditStatusResponse> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const status = await getAuditStatus(session);
        onTick?.(status);
        if (!shouldContinue(status)) {
          resolve(status);
          return;
        }
        setTimeout(() => void poll(), intervalMs);
      } catch (err) {
        reject(err);
      }
    };
    void poll();
  });
}

const VALIDATION_SETTLED_STATUSES: AuditStatus[] = [
  "ready_for_scan",
  "validation_failed",
  "processing_failed",
  "scanning",
  "generating_report",
  "completed",
  "payment_pending",
];

export function isValidationSettled(status: AuditStatus): boolean {
  return VALIDATION_SETTLED_STATUSES.includes(status);
}

export async function pollValidationUntilSettled(
  session: AuditSession,
  onTick?: (status: AuditStatusResponse) => void,
  options?: { intervalMs?: number; maxAttempts?: number },
): Promise<AuditStatusResponse> {
  const intervalMs = options?.intervalMs ?? 2000;
  const maxAttempts = options?.maxAttempts ?? 90;

  return new Promise((resolve, reject) => {
    let attempts = 0;

    const poll = async () => {
      try {
        attempts += 1;
        const status = await getAuditStatus(session);
        onTick?.(status);

        if (isValidationSettled(status.status) || status.status === "upload_failed") {
          resolve(status);
          return;
        }

        if (attempts >= maxAttempts) {
          reject(
            new ApiError(
              "Validation is taking longer than expected. For local development, set CELERY_TASK_ALWAYS_EAGER=true or run the Celery worker.",
              408,
            ),
          );
          return;
        }

        setTimeout(() => void poll(), intervalMs);
      } catch (err) {
        reject(err);
      }
    };

    void poll();
  });
}

export async function deleteUpload(session: AuditSession, uploadId: string): Promise<void> {
  await auditApiFetch<void>(`/audit/${session.auditId}/upload/${uploadId}`, {
    method: "DELETE",
    auditSession: session.sessionToken,
  });
}

export async function uploadFiles(
  session: AuditSession,
  files: File[],
  onProgress?: (filename: string, progress: number) => void,
): Promise<UploadResponse[]> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));
  const authToken = await resolveAuthToken();

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${API_URL}/audit/${session.auditId}/upload`);
    xhr.setRequestHeader("X-Audit-Session", session.sessionToken);
    if (authToken) {
      xhr.setRequestHeader("Authorization", `Bearer ${authToken}`);
    }

    xhr.upload.addEventListener("progress", (event) => {
      if (event.lengthComputable && onProgress) {
        const progress = Math.round((event.loaded / event.total) * 100);
        files.forEach((file) => onProgress(file.name, progress));
      }
    });

    xhr.addEventListener("load", () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText) as UploadResponse[]);
      } else {
        try {
          const error = JSON.parse(xhr.responseText) as { detail?: string };
          reject(new Error(error.detail ?? "Upload failed"));
        } catch {
          reject(new Error("Upload failed"));
        }
      }
    });

    xhr.addEventListener("error", () => reject(new Error("Network error during upload")));
    xhr.send(formData);
  });
}
