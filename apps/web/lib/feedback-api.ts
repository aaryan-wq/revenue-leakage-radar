import { apiFetch } from "@/lib/api";

export type FeedbackCategory = "general" | "bug" | "feature" | "billing" | "other";

export interface FeedbackPayload {
  name?: string;
  email: string;
  message: string;
  category?: FeedbackCategory;
  page_url?: string;
}

export async function submitFeedback(payload: FeedbackPayload): Promise<void> {
  await apiFetch<{ ok: boolean }>("/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
}
