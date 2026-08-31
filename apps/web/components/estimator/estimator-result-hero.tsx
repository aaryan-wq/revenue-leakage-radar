"use client";

import { useState } from "react";

import { CountUp } from "@/components/count-up";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { formatCurrency, type EstimatorBenchmarkContext, type EstimatorResult } from "@rlr/shared";

const SCENARIOS = [
  { id: "conservative", label: "Conservative", subtitle: "P10 to P50 band" },
  { id: "central", label: "Expected", subtitle: "P25 to P75 band" },
  { id: "aggressive", label: "Upside", subtitle: "P50 to P90 band" },
] as const;

interface EstimatorResultHeroProps {
  result: EstimatorResult;
  scenario: string;
  scenarioLoading: boolean;
  onScenarioChange: (scenario: string) => void;
}

export function EstimatorResultHero({
  result,
  scenario,
  scenarioLoading,
  onScenarioChange,
}: EstimatorResultHeroProps) {
  const [showGross, setShowGross] = useState(false);
  const calc = result.calculation_summary;
  const activeScenario = SCENARIOS.find((item) => item.id === scenario);
  const arr = result.arr_usd ?? result.profile_summary?.arr_usd ?? 0;
  const pctOfArr =
    calc?.pct_of_arr ?? (arr > 0 ? (result.estimate.central / arr) * 100 : 0);
  const stressP90 = result.estimate.stress_p90 ?? result.percentiles?.p90 ?? 0;
  const stressPct = arr > 0 && stressP90 > 0 ? (stressP90 / arr) * 100 : 0;
  const conditionalMean = calc?.conditional_mean ?? 0;
  const runsWithLeakage = calc?.pct_runs_with_leakage ?? 0;
  const showConditional = runsWithLeakage >= 70 && conditionalMean > result.estimate.central;
  const grossExpected = result.estimate.gross_expected ?? 0;

  return (
    <HairlineCard padding="lg" className="overflow-hidden">
      <div className="space-y-8">
        <div className="flex flex-wrap items-center justify-center gap-2">
          <Badge variant="info">Modeled estimate</Badge>
          {result.complexity?.label ? (
            <Badge variant="gray">{result.complexity.label} complexity</Badge>
          ) : null}
          {result.confidence ? <Badge variant="success">{result.confidence} confidence</Badge> : null}
        </div>

        <div className="space-y-4 text-center">
          <h1 className="text-h2 text-foreground">Recoverable revenue opportunity</h1>
          <p className="text-metric-xl tabular-nums text-foreground">
            <CountUp to={result.estimate.central} prefix="$" />
          </p>
          <p className="text-body tabular-nums text-foreground">
            Expected recoverable · {pctOfArr.toFixed(1)}% of {arr > 0 ? formatCurrency(arr) : "ARR"}
          </p>
          <p className="text-small tabular-nums text-muted-foreground">
            Modeled range {formatCurrency(result.estimate.low)} to {formatCurrency(result.estimate.high)}
            {stressP90 > 0 ? (
              <>
                {" "}
                · Stress case up to {formatCurrency(stressP90)}
                {stressPct > 0 ? ` (${stressPct.toFixed(1)}% of ARR)` : ""}
              </>
            ) : null}
          </p>
          {showConditional ? (
            <p className="text-body text-muted-foreground">
              In simulations where leakage occurred ({runsWithLeakage.toFixed(0)}% of runs), typical exposure
              was{" "}
              <span className="tabular-nums text-foreground">{formatCurrency(conditionalMean)}</span>.
            </p>
          ) : null}
          {activeScenario ? (
            <p className="text-caption text-muted-foreground">
              {activeScenario.label} band: {calc?.scenario_band_label ?? activeScenario.subtitle}. Modeled
              estimate, not an audited finding.
            </p>
          ) : null}
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <StatTile
            label="Runs with leakage"
            value={`${runsWithLeakage.toFixed(0)}%`}
            hint="Share of simulations with any modeled leakage"
          />
          <StatTile
            label="Conditional mean"
            value={conditionalMean > 0 ? formatCurrency(conditionalMean) : "—"}
            hint="Average when leakage occurred"
          />
          <StatTile
            label="Detectable range"
            value={
              result.detectable.high > 0
                ? `${formatCurrency(result.detectable.low)} to ${formatCurrency(result.detectable.high)}`
                : "—"
            }
            hint="Likely matchable from billing exports"
          />
        </div>

        {grossExpected > result.estimate.central ? (
          <div className="text-center">
            <Button
              variant="ghost"
              size="sm"
              className="min-h-[44px]"
              onClick={() => setShowGross((open) => !open)}
            >
              {showGross ? "Hide gross exposure" : "Show gross exposure"}
            </Button>
            {showGross ? (
              <p className="text-small mt-2 tabular-nums text-muted-foreground">
                Gross exposure before recoverability weighting: {formatCurrency(grossExpected)}.
              </p>
            ) : null}
          </div>
        ) : null}

        {result.benchmark_context ? (
          <BenchmarkContextPanel context={result.benchmark_context} central={result.estimate.central} />
        ) : null}

        <div className="space-y-3">
          <div className="flex flex-wrap items-center justify-center gap-2">
            {SCENARIOS.map((option) => (
              <Button
                key={option.id}
                variant={scenario === option.id ? "primary" : "secondary"}
                onClick={() => onScenarioChange(option.id)}
                disabled={scenarioLoading}
                className="min-h-[44px]"
              >
                {option.label}
              </Button>
            ))}
          </div>
          <p className="text-center text-caption text-muted-foreground">
            Scenarios change the percentile band, not your answers.
          </p>
        </div>
      </div>
    </HairlineCard>
  );
}

function StatTile({ label, value, hint }: { label: string; value: string; hint: string }) {
  return (
    <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-5 text-center">
      <p className="text-caption text-muted-foreground">{label}</p>
      <p className="text-h4 mt-2 tabular-nums text-foreground">{value}</p>
      <p className="text-small mt-1 text-muted-foreground">{hint}</p>
    </div>
  );
}

function BenchmarkContextPanel({
  context,
  central,
}: {
  context: EstimatorBenchmarkContext;
  central: number;
}) {
  return (
    <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-5 text-left">
      <p className="text-overline text-muted-foreground">Industry context</p>
      <p className="text-body mt-2 text-foreground">
        Your model: {formatCurrency(central)} ({context.model_pct_of_arr.toFixed(1)}% of ARR). Similar audited
        SaaS companies often see {(context.pct_arr_low * 100).toFixed(1)}% to{" "}
        {(context.pct_arr_high * 100).toFixed(1)}% exposure ({formatCurrency(context.low_usd)} to{" "}
        {formatCurrency(context.high_usd)}).
      </p>
      {context.may_understate ? (
        <p className="text-small mt-2 text-muted-foreground">
          Your answers suggest lower operational risk than typical at this scale. A billing scan can confirm
          whether leakage is higher in practice.
        </p>
      ) : null}
    </div>
  );
}

export function EstimatorSensitivityUpsell({ drivers }: { drivers: EstimatorResult["drivers"] }) {
  const top = (drivers ?? []).filter((d) => (d.delta_expected ?? 0) > 0).slice(0, 3);
  if (top.length === 0) return null;

  return (
    <HairlineCard padding="lg" className="space-y-4">
      <div>
        <p className="text-overline text-muted-foreground">Sensitivity</p>
        <h2 className="text-h4 mt-2">What could increase this estimate</h2>
        <p className="text-body mt-2 text-muted-foreground">
          If operational controls are weaker than you reported, modeled exposure could rise.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {top.map((driver) => (
          <div
            key={driver.key}
            className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4"
          >
            <p className="text-small font-medium text-foreground">{driver.label}</p>
            <p className="text-body mt-2 tabular-nums text-foreground">
              +{formatCurrency(driver.delta_expected ?? 0)}
            </p>
            <p className="text-caption mt-1 text-muted-foreground">Under a stressed answer scenario</p>
          </div>
        ))}
      </div>
    </HairlineCard>
  );
}

export function EstimatorIncompleteEstimateNotice({
  pendingCount,
  onAnswer,
}: {
  pendingCount: number;
  onAnswer: () => void;
}) {
  if (pendingCount <= 0) return null;

  return (
    <HairlineCard padding="md" className="border-primary/20 bg-surface-glass-subtle">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p className="text-body text-foreground">
          {pendingCount} unanswered question{pendingCount === 1 ? "" : "s"} may widen your estimate upward.
        </p>
        <Button variant="secondary" onClick={onAnswer} className="min-h-[44px] shrink-0">
          Refine estimate
        </Button>
      </div>
    </HairlineCard>
  );
}
