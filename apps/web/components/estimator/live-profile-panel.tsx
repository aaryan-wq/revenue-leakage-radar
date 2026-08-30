"use client";

import type { EstimatorComplexityPreview } from "@rlr/shared";
import { formatCurrency } from "@rlr/shared";

import { HairlineCard } from "@/components/ui/glass-card";

interface LiveProfilePanelProps {
  arrUsd?: number;
  complexity?: EstimatorComplexityPreview | null;
}

export function LiveProfilePanel({ arrUsd, complexity }: LiveProfilePanelProps) {
  return (
    <HairlineCard padding="md" className="space-y-6 sticky top-24">
      <div>
        <p className="text-overline text-muted-foreground">Your billing profile</p>
        <h3 className="text-h4 mt-2">Live preview</h3>
      </div>

      <dl className="space-y-4">
        <div>
          <dt className="text-caption text-muted-foreground">ARR</dt>
          <dd className="text-body font-medium tabular-nums">
            {arrUsd ? formatCurrency(arrUsd) : "Pending"}
          </dd>
        </div>
        {complexity ? (
          <>
            <div>
              <dt className="text-caption text-muted-foreground">Billing complexity</dt>
              <dd className="text-body font-medium">{complexity.label}</dd>
            </div>
            <div className="space-y-2">
              {(
                [
                  ["Pricing", complexity.pricing],
                  ["Contracts", complexity.contract],
                  ["Systems", complexity.systems],
                  ["Change", complexity.change],
                  ["Operations", complexity.operations],
                ] as const
              ).map(([label, score]) => (
                <div key={label}>
                  <div className="mb-1 flex justify-between text-caption">
                    <span className="text-muted-foreground">{label}</span>
                    <span className="tabular-nums">{score}/8</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-border/40">
                    <div
                      className="h-full rounded-full bg-primary transition-all"
                      style={{ width: `${(score / 8) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </>
        ) : null}
      </dl>

      <p className="text-caption text-muted-foreground">
        Complexity preview only. Leakage estimate appears after you complete the assessment.
      </p>
    </HairlineCard>
  );
}
