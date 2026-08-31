"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { ArrowRight } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { fetchShare } from "@/lib/estimator/api";
import { formatCurrency } from "@rlr/shared";

export function EstimatorShareClient({ token }: { token: string }) {
  const [data, setData] = useState<Awaited<ReturnType<typeof fetchShare>> | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void fetchShare(token)
      .then(setData)
      .catch(() => setError("This share link is unavailable or has expired."));
  }, [token]);

  if (error) {
    return (
      <div className="mx-auto max-w-marketing px-6 py-24 md:px-10">
        <HairlineCard padding="lg" className="mx-auto max-w-readable space-y-6 text-center">
          <h1 className="text-h3 text-foreground">Link unavailable</h1>
          <p className="text-body text-muted-foreground">{error}</p>
          <Link href="/saas-revenue-leakage-calculator">
            <Button className="min-h-[44px]">Run your own assessment</Button>
          </Link>
        </HairlineCard>
      </div>
    );
  }

  if (!data) return <PageLoadingSkeleton message="Loading shared estimate…" />;

  const { estimate, top_hypotheses: topHypotheses, confidence, disclaimer, arr_usd: arrUsd } = data;
  const topThree = topHypotheses.slice(0, 3);
  const mechanismAmount = (item: (typeof topThree)[number]) =>
    Math.max(item.expected ?? 0, item.high ?? 0, item.mid ?? 0);
  const maxMechanism = Math.max(...topThree.map(mechanismAmount), 1);
  const pctOfArr = arrUsd && arrUsd > 0 ? (estimate.high / arrUsd) * 100 : null;

  return (
    <div className="mx-auto max-w-marketing space-y-10 px-6 py-12 md:px-10 md:py-16">
      <Reveal>
        <div className="space-y-2 text-center">
          <p className="text-overline text-muted-foreground">Shared estimate</p>
          <h1 className="text-h2 text-foreground">Estimated recoverable revenue</h1>
        </div>
      </Reveal>

      <Reveal>
        <HairlineCard padding="lg" className="overflow-hidden">
          <div className="space-y-6">
            {confidence ? (
              <div className="flex justify-center">
                <Badge variant="success">{confidence} confidence</Badge>
              </div>
            ) : null}

            <div className="space-y-4 text-center">
              <p className="text-metric-xl tabular-nums text-foreground">
                ~{formatCurrency(estimate.high)}
                <span className="text-h4 text-muted-foreground"> /year</span>
              </p>

              {pctOfArr !== null && arrUsd ? (
                <p className="text-body tabular-nums text-muted-foreground">
                  About {pctOfArr.toFixed(1)}% of {formatCurrency(arrUsd)} ARR
                </p>
              ) : null}

              <p className="text-small text-muted-foreground">{disclaimer}</p>
            </div>
          </div>
        </HairlineCard>
      </Reveal>

      {topThree.length > 0 ? (
        <Stagger className="space-y-6">
          <div>
            <h2 className="text-h4 text-foreground">Top likely sources</h2>
            <p className="text-small mt-2 text-muted-foreground">
              These categories overlap and are not additive.
            </p>
          </div>
          {topThree.map((item) => {
            const amount = mechanismAmount(item);
            return (
            <StaggerItem key={item.hypothesis_id}>
              <HairlineCard padding="lg" className="space-y-4">
                <div className="space-y-2">
                  <h3 className="text-body font-medium text-foreground">{item.name}</h3>
                  <p className="text-metric-xl tabular-nums text-foreground">
                    ~{formatCurrency(amount)}
                    <span className="text-h4 text-muted-foreground"> /year</span>
                  </p>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-border/30">
                  <div
                    className="h-full rounded-full bg-primary/80 transition-all duration-300"
                    style={{ width: `${Math.max(8, (amount / maxMechanism) * 100)}%` }}
                  />
                </div>
              </HairlineCard>
            </StaggerItem>
            );
          })}
        </Stagger>
      ) : null}

      <Reveal>
        <HairlineCard padding="lg" className="space-y-6 border-primary/20 text-center">
          <div className="space-y-3">
            <h2 className="text-h3 text-foreground">Want your own estimate?</h2>
            <p className="mx-auto max-w-readable text-body text-muted-foreground">
              Answer a few questions about your billing operations and get a personalized leakage
              estimate in minutes.
            </p>
          </div>
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/saas-revenue-leakage-calculator/start">
              <Button className="min-h-[44px]">
                Run your own assessment
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/saas-revenue-leakage-calculator/methodology">
              <Button variant="ghost" className="min-h-[44px]">
                View methodology
              </Button>
            </Link>
          </div>
        </HairlineCard>
      </Reveal>
    </div>
  );
}
