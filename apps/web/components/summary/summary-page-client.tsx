"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

import { FreeSummaryView } from "@/components/summary/free-summary-view";
import { useRegisterFunnelAction } from "@/components/audit/audit-funnel-actions";
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
import { getDashboard, getSummary } from "@/lib/report-api";
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

  const handleCompleteAudit = useCallback(async () => {
    if (!isSignedIn) {
      toast.error("Sign in to save this audit to your workspace.");
      return;
    }

    setIsCompleting(true);
    try {
      const token = await getToken();
      if (!token) {
        toast.error("Sign in to save this audit to your workspace.");
        return;
      }
      await saveCompletedAuditOnExit(token, { auditId: summary?.audit_id });
      await queryClient.invalidateQueries({
        queryKey: queryKeys.dashboard,
        refetchType: "all",
      });

      const savedAuditId = summary?.audit_id;
      if (savedAuditId) {
        const dashboard = await getDashboard(token);
        const savedAuditVisible = dashboard.audits.some((audit) => audit.audit_id === savedAuditId);
        if (!savedAuditVisible) {
          throw new Error(
            "Audit could not be added to your workspace. Please try again or contact support.",
          );
        }
        queryClient.setQueryData(queryKeys.dashboard, dashboard);
      }

      toast.success("Audit saved to your workspace.");
      router.push(WORKSPACE_EXIT_HREF);
    } catch (err) {
      const message =
        err instanceof Error ? err.message : "Unable to save audit. Please try again.";
      toast.error(message);
    } finally {
      setIsCompleting(false);
    }
  }, [getToken, isSignedIn, queryClient, router, summary?.audit_id]);

  useRegisterFunnelAction(
    summary && !isLoading && !error
      ? {
          label: isCompleting ? "Saving…" : "Complete Audit",
          disabled: isCompleting,
          loading: isCompleting,
          onClick: handleCompleteAudit,
        }
      : null,
  );

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
        <FreeSummaryView summary={summary} onUnlocked={() => void loadSummary()} />
      )}
    </PageShell>
  );
}
