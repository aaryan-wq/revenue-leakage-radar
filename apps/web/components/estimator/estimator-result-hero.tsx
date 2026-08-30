"use client";

import { CountUp } from "@/components/count-up";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { formatCurrency, type EstimatorResult } from "@rlr/shared";

const SCENARIOS = [
  { id: "conservative", label: "Low case", subtitle: "P10 to P50" },
  { id: "central", label: "Expected", subtitle: "P25 to P75" },
  { id: "aggressive", label: "Stress", subtitle: "P75 to P90" },
] as const;

interface EstimatorResultHeroProps {
  result: EstimatorResult;
  scenario: string;
  scenarioLoading: boolean;
  onScenarioChange: (scenario: string) => void;
}

function percentilePosition(value: number, min: number, max: number): number {
  if (max <= min) return 50;
  return Math.min(100, Math.max(0, ((value - min) / (max - min)) * 100));
}

export function EstimatorResultHero({
  result,
  scenario,
  scenarioLoading,
  onScenarioChange,
}: EstimatorResultHeroProps) {
  const calc = result.calculation_summary;
  const pct = result.percentiles ?? {};
  const p10 = pct.p10 ?? result.estimate.low;
  const p25 = pct.p25 ?? result.estimate.low;
  const p50 = pct.p50 ?? result.estimate.median_run ?? result.estimate.central;
  const p75 = pct.p75 ?? result.estimate.high;
  const p90 = result.estimate.stress_p90 ?? pct.p90 ?? result.estimate.high;
  const arr = result.arr_usd ?? result.profile_summary?.arr_usd ?? 0;
  const pctOfArr =
    calc?.pct_of_arr ?? (arr > 0 ? (result.estimate.central / arr) * 100 : 0);
  const stressPct = arr > 0 ? (p90 / arr) * 100 : result.estimate.headline_pct ?? 0;
  const recoverable = result.recoverable?.expected ?? result.estimate.recoverable ?? 0;
  const activeScenario = SCENARIOS.find((item) => item.id === scenario);
  const bandMax = Math.max(p90, result.estimate.high, p75, 1);
  const markerPositions = {
    p25: percentilePosition(p25, p10, bandMax),
    p50: percentilePosition(p50, p10, bandMax),
    p75: percentilePosition(p75, p10, bandMax),
    p90: percentilePosition(p90, p10, bandMax),
  };

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

        <div className="space-y-3 text-center">
          <p className="text-overline text-muted-foreground">Potential revenue at risk</p>
          <p className="text-metric-xl tabular-nums text-foreground">
            <CountUp to={result.estimate.low} prefix="$" /> to{" "}
            <CountUp to={result.estimate.high} prefix="$" />
          </p>
          <p className="text-body text-muted-foreground">
            {arr > 0 ? (
              <>
                Based on {formatCurrency(arr)} ARR. Expected{" "}
                <span className="tabular-nums text-foreground">{pctOfArr.toFixed(1)}%</span> leakage, with stress
                scenarios up to{" "}
                <span className="tabular-nums text-foreground">{stressPct.toFixed(1)}%</span>.
              </>
            ) : (
              <>Modeled from your billing profile and operational answers.</>
            )}
          </p>
        </div>

        <div className="mx-auto max-w-readable space-y-3">
          <div className="relative h-3 overflow-hidden rounded-full bg-border/30">
            <div
              className="absolute inset-y-0 left-0 rounded-full bg-primary/25"
              style={{ width: `${markerPositions.p75}%` }}
            />
            <div
              className="absolute inset-y-0 rounded-full bg-primary/55"
              style={{ left: `${markerPositions.p25}%`, width: `${markerPositions.p75 - markerPositions.p25}%` }}
            />
            {(["p25", "p50", "p75", "p90"] as const).map((key) => (
              <span
                key={key}
                className="absolute top-1/2 h-4 w-0.5 -translate-y-1/2 rounded-full bg-primary"
                style={{ left: `${markerPositions[key]}%` }}
              />
            ))}
          </div>
          <div className="flex justify-between text-caption tabular-nums text-muted-foreground">
            <span>P10 {formatCurrency(p10)}</span>
            <span>P90 {formatCurrency(p90)}</span>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-3">
          <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-5 text-center">
            <p className="text-caption text-muted-foreground">Expected recoverable</p>
            <p className="text-h4 mt-2 tabular-nums text-foreground">
              {formatCurrency(result.estimate.central)}
            </p>
            <p className="text-small mt-1 tabular-nums text-muted-foreground">{pctOfArr.toFixed(1)}% of ARR</p>
          </div>
          <div className="rounded-xl border border-primary/20 bg-surface-glass-subtle p-5 text-center">
            <p className="text-caption text-muted-foreground">Stress case (P90)</p>
            <p className="text-h4 mt-2 tabular-nums text-foreground">{formatCurrency(p90)}</p>
            <p className="text-small mt-1 tabular-nums text-muted-foreground">{stressPct.toFixed(1)}% of ARR</p>
          </div>
          <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-5 text-center">
            <p className="text-caption text-muted-foreground">Recoverable now</p>
            <p className="text-h4 mt-2 tabular-nums text-foreground">
              {recoverable > 0 ? formatCurrency(recoverable) : formatCurrency(result.estimate.central)}
            </p>
            <p className="text-small mt-1 text-muted-foreground">
              {recoverable > 0 ? "Likely fixable with billing exports" : "Expected recoverable baseline"}
            </p>
          </div>
        </div>

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
          {activeScenario ? (
            <p className="text-center text-caption text-muted-foreground">
              {activeScenario.label} view uses the {activeScenario.subtitle} band. Modeled estimate, not an audited
              finding.
            </p>
          ) : null}
        </div>
      </div>
    </HairlineCard>
  );
}

export function EstimatorResultMethodology({
  result,
  calc,
}: {
  result: EstimatorResult;
  calc: NonNullable<EstimatorResult["calculation_summary"]>;
}) {
  const topMechanisms = result.top_hypotheses.slice(0, 3);

  return (
    <HairlineCard padding="lg" className="space-y-6">
      <div>
        <p className="text-overline text-muted-foreground">Model calculation</p>
        <h2 className="text-h4 mt-2">How we modeled this</h2>
        <p className="text-body mt-3 max-w-readable text-muted-foreground">
          {calc.explanation_bullets[0] ??
            `${calc.simulation_count.toLocaleString()} Monte Carlo simulations across 27 billing verification rules.`}
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4">
          <p className="text-caption text-muted-foreground">Simulations</p>
          <p className="text-body mt-1 tabular-nums text-foreground">
            {calc.simulation_count.toLocaleString()}
          </p>
        </div>
        <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4">
          <p className="text-caption text-muted-foreground">Runs with leakage</p>
          <p className="text-body mt-1 tabular-nums text-foreground">{calc.pct_runs_with_leakage.toFixed(0)}%</p>
        </div>
        <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4">
          <p className="text-caption text-muted-foreground">Monthly band</p>
          <p className="text-body mt-1 tabular-nums text-foreground">
            {formatCurrency(result.monthly.low)} to {formatCurrency(result.monthly.high)}
          </p>
        </div>
        <div className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4">
          <p className="text-caption text-muted-foreground">Detectable range</p>
          <p className="text-body mt-1 tabular-nums text-foreground">
            {formatCurrency(result.detectable.low)} to {formatCurrency(result.detectable.high)}
          </p>
        </div>
      </div>

      {topMechanisms.length > 0 ? (
        <div className="space-y-3">
          <p className="text-small font-medium text-foreground">Largest modeled mechanisms</p>
          <div className="grid gap-3 sm:grid-cols-3">
            {topMechanisms.map((item) => (
              <div
                key={item.hypothesis_id}
                className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4"
              >
                <p className="text-caption text-muted-foreground">{item.share_of_total.toFixed(0)}% of total</p>
                <p className="text-small mt-1 text-foreground">{item.name}</p>
                <p className="text-body mt-2 tabular-nums text-foreground">{formatCurrency(item.expected)}</p>
              </div>
            ))}
          </div>
        </div>
      ) : null}
    </HairlineCard>
  );
}
