"use client";

import { useEffect, useState } from "react";

import { HairlineCard } from "@/components/ui/glass-card";
import { fetchResult } from "@/lib/estimator/api";
import { formatCurrency, type EstimatorResult } from "@rlr/shared";

interface EstimatorVerificationComparisonProps {
  assessmentId: string;
  verifiedArr: number;
}

export function EstimatorVerificationComparison({
  assessmentId,
  verifiedArr,
}: EstimatorVerificationComparisonProps) {
  const [estimate, setEstimate] = useState<EstimatorResult | null>(null);

  useEffect(() => {
    void fetchResult(assessmentId).then(setEstimate).catch(() => setEstimate(null));
  }, [assessmentId]);

  if (!estimate) return null;

  const inRange =
    verifiedArr >= estimate.estimate.low && verifiedArr <= estimate.estimate.high;

  return (
    <HairlineCard padding="lg" className="space-y-4">
      <h2 className="text-h4">Your estimate vs. verified leakage</h2>
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-caption text-muted-foreground">Estimator (modeled)</p>
          <p className="text-body tabular-nums">
            {formatCurrency(estimate.estimate.low)} to {formatCurrency(estimate.estimate.high)}
          </p>
        </div>
        <div>
          <p className="text-caption text-muted-foreground">Verified (billing scan)</p>
          <p className="text-body tabular-nums">{formatCurrency(verifiedArr)}</p>
        </div>
      </div>
      <p className="text-small text-muted-foreground">
        {inRange
          ? "Your verified result fell within the estimator modeled range."
          : "Your verified result fell outside the modeled range. This helps calibrate future estimates."}
      </p>
    </HairlineCard>
  );
}
