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
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getStoredAuditSession } from "@/lib/audit-session";
import { getSummary } from "@/lib/report-api";
import type { FreeSummaryResponse } from "@rlr/shared";

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

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading revenue summary…" />;
  }

  if (error || !summary) {
    return (
      <GlassCard padding="md" className="border-error/20 bg-error-bg text-center">
        <p className="text-body text-gray-700">{error ?? "Summary unavailable."}</p>
        <Button className="mt-6" onClick={() => void loadSummary()}>
          Retry
        </Button>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-16">
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
      <div>
        <Link
          href="/analysis"
          className="text-small text-gray-500 hover:text-gray-900 transition-colors"
        >
          ← Back to Analysis
        </Link>
      </div>
    </div>
  );
}
