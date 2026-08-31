"use client";

import { useEffect, useState } from "react";

import { HairlineCard } from "@/components/ui/glass-card";
import { fetchResult } from "@/lib/estimator/api";
import { formatCurrency, getEstimatorHeadlineUsd, type EstimatorResult } from "@rlr/shared";

export function AssessmentContextBanner({ assessmentId }: { assessmentId: string }) {
  const [result, setResult] = useState<EstimatorResult | null>(null);

  useEffect(() => {
    void fetchResult(assessmentId)
      .then(setResult)
      .catch(() => setResult(null));
  }, [assessmentId]);

  if (!result) return null;

  const names = result.top_hypotheses.slice(0, 3).map((h) => h.name.toLowerCase()).join(", ");

  return (
    <HairlineCard padding="md" className="mb-8 border-primary/20 bg-surface-glass-subtle">
      <p className="text-overline text-muted-foreground">From your leakage assessment</p>
      <p className="text-body mt-2 text-foreground">
        Based on your assessment (~{formatCurrency(getEstimatorHeadlineUsd(result))} modeled exposure), we will prioritize
        checks related to {names || "your top billing risk areas"} during the scan presentation.
      </p>
      <p className="text-caption mt-2 text-muted-foreground">
        This does not change scan logic or findings.
      </p>
    </HairlineCard>
  );
}
