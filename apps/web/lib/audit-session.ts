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

import { apiFetch } from "./api";

const SESSION_KEY = "rlr_audit_session";
const AUDIT_ID_KEY = "rlr_audit_id";

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
}

export async function createAuditSession(): Promise<AuditSession> {
  const response = await apiFetch<AuditCreateResponse>("/audit", {
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
  return apiFetch<AuditStatusResponse>(`/audit/${session.auditId}`, {
    auditSession: session.sessionToken,
  });
}

export async function startValidation(session: AuditSession): Promise<ValidateResponse> {
  return apiFetch<ValidateResponse>(`/audit/${session.auditId}/validate`, {
    method: "POST",
    auditSession: session.sessionToken,
  });
}

export async function getValidationReport(
  session: AuditSession,
): Promise<ValidationReportResponse> {
  return apiFetch<ValidationReportResponse>(`/audit/${session.auditId}/validation`, {
    auditSession: session.sessionToken,
  });
}

export function isProcessingStatus(status: AuditStatus): boolean {
  return PROCESSING_STATUSES.includes(status);
}

export function isScanProcessingStatus(status: AuditStatus): boolean {
  return SCAN_PROCESSING_STATUSES.includes(status);
}

export async function startScan(session: AuditSession): Promise<ScanResponse> {
  return apiFetch<ScanResponse>(`/audit/${session.auditId}/scan`, {
    method: "POST",
    auditSession: session.sessionToken,
  });
}

export async function getScanReport(session: AuditSession): Promise<ScanReportResponse> {
  return apiFetch<ScanReportResponse>(`/audit/${session.auditId}/scan`, {
    auditSession: session.sessionToken,
  });
}

export async function pollScanUntil(
  session: AuditSession,
  shouldContinue: (report: ScanReportResponse) => boolean,
  onTick?: (report: ScanReportResponse) => void,
  intervalMs = 2000,
): Promise<ScanReportResponse> {
  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const report = await getScanReport(session);
        onTick?.(report);
        if (!shouldContinue(report)) {
          resolve(report);
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

export async function uploadFiles(
  session: AuditSession,
  files: File[],
  onProgress?: (filename: string, progress: number) => void,
): Promise<UploadResponse[]> {
  const formData = new FormData();
  files.forEach((file) => formData.append("files", file));

  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open("POST", `${process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"}/audit/${session.auditId}/upload`);
    xhr.setRequestHeader("X-Audit-Session", session.sessionToken);

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
