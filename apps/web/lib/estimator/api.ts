import type {
  EstimatorAssessmentState,
  EstimatorQuestion,
  EstimatorResult,
} from "@rlr/shared";

import { apiFetch } from "@/lib/api";

const SESSION_KEY = "rlr_estimator_session";
const ASSESSMENT_KEY = "rlr_estimator_assessment_id";

export function clearAssessmentSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ASSESSMENT_KEY);
  localStorage.removeItem(SESSION_KEY);
}

export function getStoredAssessmentId(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ASSESSMENT_KEY);
}

export function storeAssessmentSession(assessmentId: string, sessionToken: string): void {
  localStorage.setItem(ASSESSMENT_KEY, assessmentId);
  localStorage.setItem(SESSION_KEY, sessionToken);
}

export function storeAssessmentId(assessmentId: string): void {
  if (typeof window === "undefined") return;
  localStorage.setItem(ASSESSMENT_KEY, assessmentId);
}

export function getStoredSessionToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(SESSION_KEY);
}

export async function createAssessment(anonymousId?: string) {
  return apiFetch<{ assessment_id: string; session_token: string }>("/estimator/assessments", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ anonymous_id: anonymousId ?? null }),
  });
}

export async function fetchQuestionnaire() {
  return apiFetch<{ version: string; sections: { id: string; label: string }[]; questions: EstimatorQuestion[] }>(
    "/estimator/questionnaire",
  );
}

export async function fetchAssessment(assessmentId: string) {
  return apiFetch<EstimatorAssessmentState & { complexity_preview?: EstimatorAssessmentState["complexity_preview"] }>(
    `/estimator/assessments/${assessmentId}`,
  );
}

export async function patchAnswers(
  assessmentId: string,
  answers: {
    question_id: string;
    value_numeric?: number;
    value_boolean?: boolean;
    value_text?: string;
    value_enum?: string;
    value_json?: string[];
  }[],
) {
  return apiFetch<EstimatorAssessmentState>(`/estimator/assessments/${assessmentId}/answers`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ answers }),
  });
}

export async function validateAssessment(assessmentId: string) {
  return apiFetch<{ warnings: { code: string; message: string }[]; contradictions: { code: string; message: string }[] }>(
    `/estimator/assessments/${assessmentId}/validate`,
    { method: "POST" },
  );
}

export async function calculateAssessment(assessmentId: string, scenario = "aggressive") {
  return apiFetch<EstimatorResult>(`/estimator/assessments/${assessmentId}/calculate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ scenario }),
    timeoutMs: 60_000,
  });
}

export async function fetchResult(assessmentId: string) {
  return apiFetch<EstimatorResult>(`/estimator/assessments/${assessmentId}/result`);
}

export async function saveLead(
  assessmentId: string,
  payload: { email: string; company_name?: string; role?: string; scan_intent?: boolean },
) {
  return apiFetch<{ lead_id: string; lead_score: number; email_sent: boolean }>(
    `/estimator/assessments/${assessmentId}/lead`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    },
  );
}

export async function createShareLink(assessmentId: string) {
  return apiFetch<{ share_token: string; share_path: string }>(
    `/estimator/assessments/${assessmentId}/share`,
    { method: "POST" },
  );
}

export async function fetchShare(token: string) {
  return apiFetch<{
    disclaimer: string;
    arr_usd: number | null;
    estimate: EstimatorResult["estimate"];
    top_hypotheses: EstimatorResult["top_hypotheses"];
    confidence: string;
  }>(`/estimator/share/${token}`);
}
