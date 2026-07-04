"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { CoverageSection } from "@/components/summary/coverage-section";
import { LockedPreview } from "@/components/summary/locked-preview";
import { OpportunityBreakdown } from "@/components/summary/opportunity-breakdown";
import { SummaryHero } from "@/components/summary/summary-hero";
import { UnlockCta } from "@/components/summary/unlock-cta";
import { VerificationChecklist } from "@/components/summary/verification-checklist";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageShell } from "@/components/ui/page-loading";
import { getStoredAuditSession } from "@/lib/audit-session";
import { captureAuditEvent } from "@/lib/analytics/client";
import { getSummary } from "@/lib/report-api";
import { useTrackOnce } from "@/lib/analytics/hooks";
import type { FreeSummaryResponse } from "@rlr/shared";
import { AnalyticsEvents } from "@rlr/shared";

export function SummaryPageClient() {
  const router = useRouter();
  const [summary, setSummary] = useState<FreeSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
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
    <div className="mx-auto max-w-report space-y-0">
      <SummaryHero summary={summary} />
      <OpportunityBreakdown items={summary.opportunity_breakdown} />
      <VerificationChecklist checks={summary.verification_checks} />
      <CoverageSection coverage={summary.coverage} />
      <LockedPreview items={summary.locked_preview} />
      <UnlockCta
        reportId={summary.report_id}
        purchased={summary.purchased}
        onUnlocked={() => void loadSummary()}
      />
      <div className="border-t border-line pt-10">
        <Link
          href="/analysis"
          className="text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          ← Back to analysis
        </Link>
      </div>
    </div>
      )}
    </PageShell>
  );
}
