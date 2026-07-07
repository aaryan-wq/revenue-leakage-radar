"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

import { FreeSummaryView } from "@/components/summary/free-summary-view";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageShell } from "@/components/ui/page-loading";
import { useAppAuth } from "@/lib/app-auth";
import {
  getStoredAuditSession,
  saveCompletedAuditOnExit,
  WORKSPACE_EXIT_HREF,
} from "@/lib/audit-session";
import { captureAuditEvent } from "@/lib/analytics/client";
import { getSummary } from "@/lib/report-api";
import { queryKeys } from "@/lib/query/keys";
import { useTrackOnce } from "@/lib/analytics/hooks";
import { toast } from "@/lib/toast";
import type { FreeSummaryResponse } from "@rlr/shared";
import { AnalyticsEvents } from "@rlr/shared";

export function SummaryPageClient() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { getToken, isSignedIn } = useAppAuth();
  const [summary, setSummary] = useState<FreeSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isCompleting, setIsCompleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) {
      router.replace("/upload");
      return;
    }

    try {
      const data = await getSummary(session.auditId, session);
      setSummary(data);
    } catch {
      setError("Unable to load revenue summary. Please try again.");
    } finally {
      setIsLoading(false);
    }
  }, [router]);

  useEffect(() => {
    void loadSummary();
  }, [loadSummary]);

  useTrackOnce(
    AnalyticsEvents.FREE_SUMMARY_VIEWED,
    summary
      ? {
          audit_id: summary.audit_id,
          estimated_annual_leakage: summary.recoverable_arr,
          findings_total: summary.finding_count,
          confidence_score: summary.confidence ?? undefined,
          rules_executed: summary.rules_completed,
          crm_present: summary.coverage.crm_present,
        }
      : undefined,
    Boolean(summary),
  );

  const handleCompleteAudit = async () => {
    if (!isSignedIn) {
      toast.error("Sign in to save this audit to your workspace.");
      return;
    }

    setIsCompleting(true);
    try {
      const token = await getToken();
      await saveCompletedAuditOnExit(token);
      void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
      toast.success("Audit saved to your workspace.");
      router.push(WORKSPACE_EXIT_HREF);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to save audit. Please try again.";
      toast.error(message);
    } finally {
      setIsCompleting(false);
    }
  };

  if (!isLoading && (error || !summary)) {
    return (
      <div className="mx-auto max-w-report">
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-body text-foreground">{error ?? "Summary unavailable."}</p>
          <Button
            className="mt-6"
            onClick={() => {
              const session = getStoredAuditSession();
              if (session) {
                captureAuditEvent(AnalyticsEvents.FREE_SUMMARY_REFRESHED, session.auditId);
              }
              void loadSummary();
            }}
          >
            Retry
          </Button>
        </GlassCard>
      </div>
    );
  }

  return (
    <PageShell isLoading={isLoading} message="Loading free audit…" variant="report">
      {summary && (
        <FreeSummaryView
          summary={summary}
          onUnlocked={() => void loadSummary()}
          headerAction={
            <Button onClick={() => void handleCompleteAudit()} disabled={isCompleting}>
              {isCompleting ? "Saving…" : "Complete Audit"}
            </Button>
          }
          footer={
            <div className="border-t border-line pt-10">
              <Link
                href="/analysis"
                className="text-sm text-muted-foreground transition-colors hover:text-foreground"
              >
                ← Back to analysis
              </Link>
            </div>
          }
        />
      )}
    </PageShell>
  );
}
