"use client";

import { motion } from "framer-motion";

import type { AvailableRule, CoverageAnalysis } from "@rlr/shared";
import { CheckCircle2, Info } from "lucide-react";

import { HairlineCard } from "@/components/ui/glass-card";
import { cn } from "@/lib/utils";

interface CoverageAnalysisPanelProps {
  coverage: CoverageAnalysis | null | undefined;
  compact?: boolean;
}

function RulesAvailableHover({
  rulesAvailable,
  rulesTotal,
  availableRules,
}: {
  rulesAvailable: number;
  rulesTotal: number;
  availableRules: AvailableRule[];
}) {
  return (
    <div className="group relative w-fit">
      <button
        type="button"
        className="mt-1 block cursor-help text-left font-heading text-2xl tracking-tight tabular-nums text-foreground underline decoration-dotted decoration-muted-foreground/50 underline-offset-4 transition-colors hover:text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
        aria-describedby="rules-available-popover"
      >
        {rulesAvailable} / {rulesTotal} Rules Available
      </button>

      <div
        id="rules-available-popover"
        role="tooltip"
        className={cn(
          "pointer-events-none absolute left-0 top-full z-50 mt-2 w-[min(calc(100vw-3rem),18rem)]",
          "rounded-xl border border-line bg-card p-4 shadow-[0_16px_40px_-20px_rgba(0,0,0,0.35)]",
          "opacity-0 transition-opacity duration-200",
          "group-hover:pointer-events-auto group-hover:opacity-100",
          "group-focus-within:pointer-events-auto group-focus-within:opacity-100",
        )}
      >
        <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
          Available checks
        </p>
        {availableRules.length > 0 ? (
          <ul className="mt-3 max-h-56 space-y-2.5 overflow-y-auto">
            {availableRules.map((rule) => (
              <li key={rule.name} className="flex items-start gap-2 text-sm">
                {rule.status === "partial" ? (
                  <Info className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" strokeWidth={1.75} />
                ) : (
                  <CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-primary" strokeWidth={1.75} />
                )}
                <span>
                  <span className="text-foreground">{rule.name}</span>
                  {rule.note && (
                    <span className="mt-0.5 block text-xs text-muted-foreground">{rule.note}</span>
                  )}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="mt-3 text-sm text-muted-foreground">No checks available yet.</p>
        )}
      </div>
    </div>
  );
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  return (
    <div>
      <div className="flex items-center justify-between gap-4">
        <span className="text-sm text-foreground">{label}</span>
        <span className="text-sm font-medium tabular-nums text-foreground">{score}%</span>
      </div>
      <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-secondary">
        <div
          className="h-full rounded-full bg-primary transition-all duration-300"
          style={{ width: `${Math.min(100, Math.max(0, score))}%` }}
        />
      </div>
    </div>
  );
}

export function CoverageAnalysisPanel({ coverage, compact = false }: CoverageAnalysisPanelProps) {
  if (!coverage) {
    return (
      <HairlineCard padding="sm">
        <p className="text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
          Coverage Analysis
        </p>
        <p className="mt-3 text-sm leading-relaxed text-muted-foreground">
          Upload at least one billing export to see rule coverage and confidence estimates.
        </p>
      </HairlineCard>
    );
  }

  const categoryScores = coverage.category_scores.filter((item) => item.category !== "overall");
  const topUnlock = coverage.unlock_hints[0];

  return (
    <div className="grid gap-6 lg:grid-cols-2">
      <motion.div
        key={`${coverage.rules_available}-${coverage.estimated_confidence}`}
        initial={{ opacity: 0.6 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.25 }}
      >
        <HairlineCard padding="sm">
        <p className="text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
          Coverage Analysis
        </p>

        <div className="mt-5">
          <p className="text-sm font-medium text-foreground">Billing Data Received</p>
          {coverage.billing_data_received.length > 0 ? (
            <ul className="mt-3 space-y-2">
              {coverage.billing_data_received.map((item) => (
                <li key={item} className="flex items-center gap-2 text-sm text-foreground">
                  <CheckCircle2 className="h-4 w-4 shrink-0 text-primary" strokeWidth={1.75} />
                  {item}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-2 text-sm text-muted-foreground">No billing entities detected yet.</p>
          )}
        </div>

        <div className="mt-6 border-t border-line pt-5">
          <p className="text-sm text-muted-foreground">Coverage</p>
          <RulesAvailableHover
            rulesAvailable={coverage.rules_available}
            rulesTotal={coverage.rules_total}
            availableRules={coverage.available_rules ?? []}
          />
        </div>

        {coverage.unavailable_rules.length > 0 && !compact && (
          <div className="mt-6 border-t border-line pt-5">
            <p className="text-sm font-medium text-foreground">Unavailable</p>
            <ul className="mt-3 space-y-3">
              {coverage.unavailable_rules.slice(0, 6).map((rule) => (
                <li key={rule.name} className="text-sm">
                  <span className="text-foreground">{rule.name}</span>
                  <span className="mt-0.5 block text-muted-foreground">({rule.reason})</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        <div className="mt-6 border-t border-line pt-5">
          <p className="text-sm text-muted-foreground">Estimated Confidence</p>
          <p className="mt-1 font-heading text-3xl tracking-tight tabular-nums text-foreground">
            {coverage.estimated_confidence}%
          </p>
        </div>
      </HairlineCard>
      </motion.div>

      {!compact && (
        <HairlineCard padding="sm">
          <p className="text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
            Revenue Leakage Coverage
          </p>
          <div className="mt-5 space-y-4">
            {categoryScores.map((item) => (
              <ScoreBar key={item.category} label={item.label} score={item.score} />
            ))}
          </div>
        </HairlineCard>
      )}

      {topUnlock && (
        <p className="text-sm leading-relaxed text-muted-foreground lg:col-span-2">
          Upload{" "}
          <span className="text-foreground">{topUnlock.label.toLowerCase()}</span> to unlock{" "}
          {topUnlock.rules_unlocked} more check{topUnlock.rules_unlocked === 1 ? "" : "s"}.
        </p>
      )}
    </div>
  );
}
