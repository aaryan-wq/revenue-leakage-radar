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
    <aside className="hidden md:block">
      <HairlineCard padding="md" className="sticky top-32 space-y-6">
        <div>
          <p className="text-overline text-muted-foreground">Live preview</p>
          <h3 className="text-h4 mt-2">Your profile</h3>
        </div>

        <dl className="space-y-5">
          <div>
            <dt className="text-caption text-muted-foreground">ARR</dt>
            <dd className="mt-1 text-body font-medium tabular-nums">
              {arrUsd ? formatCurrency(arrUsd) : "Pending"}
            </dd>
          </div>
          {complexity ? (
            <>
              <div>
                <dt className="text-caption text-muted-foreground">Billing complexity</dt>
                <dd className="mt-1 text-body font-medium">{complexity.label}</dd>
              </div>
              <div className="space-y-3">
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
                    <div className="h-1 overflow-hidden rounded-full bg-border/30">
                      <div
                        className="h-full rounded-full bg-primary/80 transition-all"
                        style={{ width: `${(score / 8) * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </>
          ) : null}
        </dl>
      </HairlineCard>
    </aside>
  );
}
