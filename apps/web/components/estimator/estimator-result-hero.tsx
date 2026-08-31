"use client";

import { CountUp } from "@/components/count-up";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { formatCurrency, type EstimatorBenchmarkContext, type EstimatorResult } from "@rlr/shared";

interface EstimatorResultHeroProps {
  result: EstimatorResult;
}

export function EstimatorResultHero({ result }: EstimatorResultHeroProps) {
  const arr = result.arr_usd ?? result.profile_summary?.arr_usd ?? 0;
  const high = result.estimate.high;
  const pctOfArr = arr > 0 ? (high / arr) * 100 : 0;

  return (
    <HairlineCard padding="lg" className="overflow-hidden">
      <div className="space-y-6">
        {result.confidence ? (
          <div className="flex justify-center">
            <Badge variant="success">{result.confidence} confidence</Badge>
          </div>
        ) : null}

        <div className="space-y-4 text-center">
          <h1 className="text-h2 text-foreground">Estimated recoverable revenue</h1>
          <p className="text-metric-xl tabular-nums text-foreground">
            <CountUp to={high} prefix="~$" />
            <span className="text-h4 text-muted-foreground"> /year</span>
          </p>
          {arr > 0 ? (
            <p className="text-body tabular-nums text-muted-foreground">
              About {pctOfArr.toFixed(1)}% of your {formatCurrency(arr)} ARR
            </p>
          ) : null}
          <p className="text-small text-muted-foreground">
            Estimate based on your answers, not billing records.
          </p>
        </div>

        {result.benchmark_context ? (
          <BenchmarkContextLine context={result.benchmark_context} high={high} arr={arr} />
        ) : null}
      </div>
    </HairlineCard>
  );
}

function BenchmarkContextLine({
  context,
  high,
  arr,
}: {
  context: EstimatorBenchmarkContext;
  high: number;
  arr: number;
}) {
  const pct = arr > 0 ? (high / arr) * 100 : context.model_pct_of_arr;
  return (
    <p className="text-center text-small text-muted-foreground">
      Similar SaaS companies often see {(context.pct_arr_low * 100).toFixed(1)}% to{" "}
      {(context.pct_arr_high * 100).toFixed(1)}% of ARR ({formatCurrency(context.low_usd)} to{" "}
      {formatCurrency(context.high_usd)}). Your estimate is {pct.toFixed(1)}% of ARR.
      {context.may_understate
        ? " A billing scan can confirm whether leakage is higher in practice."
        : null}
    </p>
  );
}

export function EstimatorSensitivityUpsell({ drivers }: { drivers: EstimatorResult["drivers"] }) {
  const top = (drivers ?? []).filter((d) => (d.delta_expected ?? 0) > 0).slice(0, 3);
  if (top.length === 0) return null;

  return (
    <HairlineCard padding="lg" className="space-y-4">
      <div>
        <h2 className="text-h4 text-foreground">Could be higher if controls are weaker</h2>
        <p className="text-body mt-2 text-muted-foreground">
          If your billing operations are less controlled than you reported, exposure could rise.
        </p>
      </div>
      <div className="grid gap-4 sm:grid-cols-3">
        {top.map((driver) => (
          <div
            key={driver.key}
            className="rounded-xl border border-border/40 bg-surface-glass-subtle p-4"
          >
            <p className="text-small font-medium text-foreground">{driver.label}</p>
            <p className="text-metric-xl mt-2 tabular-nums text-foreground">
              +{formatCurrency(driver.delta_expected ?? 0)}
            </p>
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
          A few unanswered questions may raise this estimate.
        </p>
        <Button variant="secondary" onClick={onAnswer} className="min-h-[44px] shrink-0">
          Answer now
        </Button>
      </div>
    </HairlineCard>
  );
}
