import type { AuditCreateResponse, AuditStatusResponse, UploadResponse } from "@rlr/shared";

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
