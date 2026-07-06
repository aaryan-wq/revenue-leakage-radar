"use client";

import type { ReactNode } from "react";

import { CoverageSection } from "@/components/summary/coverage-section";
import { LockedPreview } from "@/components/summary/locked-preview";
import { OpportunityBreakdown } from "@/components/summary/opportunity-breakdown";
import { SummaryHero } from "@/components/summary/summary-hero";
import { UnlockCta } from "@/components/summary/unlock-cta";
import { VerificationChecklist } from "@/components/summary/verification-checklist";
import type { FreeSummaryResponse } from "@rlr/shared";

interface FreeSummaryViewProps {
  summary: FreeSummaryResponse;
  onUnlocked?: () => void;
  footer?: ReactNode;
}

export function FreeSummaryView({ summary, onUnlocked, footer }: FreeSummaryViewProps) {
  return (
    <div className="mx-auto max-w-report space-y-0">
      <SummaryHero summary={summary} />
      <OpportunityBreakdown items={summary.opportunity_breakdown} />
      <VerificationChecklist checks={summary.verification_checks} />
      <CoverageSection coverage={summary.coverage} />
      <LockedPreview items={summary.locked_preview} />
      <UnlockCta
        reportId={summary.report_id}
        purchased={summary.purchased}
        onUnlocked={onUnlocked}
      />
      {footer}
    </div>
  );
}
