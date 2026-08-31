"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

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
      <div className="mx-auto max-w-readable px-6 py-16 md:px-10">
        <HairlineCard padding="lg" className="space-y-4 text-center">
          <p className="text-body text-muted-foreground">{error}</p>
          <Link href="/saas-revenue-leakage-calculator">
            <Button className="min-h-[44px]">Run your own assessment</Button>
          </Link>
        </HairlineCard>
      </div>
    );
  }

  if (!data) return <PageLoadingSkeleton message="Loading shared estimate…" />;

  const topThree = data.top_hypotheses.slice(0, 3);

  return (
    <div className="mx-auto max-w-readable px-6 py-16 md:px-10">
      <HairlineCard padding="lg" className="space-y-6 text-center">
        <h1 className="text-h2 text-foreground">Estimated recoverable revenue</h1>
        <p className="text-metric-xl tabular-nums text-foreground">
          ~{formatCurrency(data.estimate.high)}
          <span className="text-h4 text-muted-foreground"> /year</span>
        </p>
        <p className="text-small text-muted-foreground">{data.disclaimer}</p>
        {topThree.length > 0 ? (
          <div className="space-y-2 text-left">
            <p className="text-caption text-muted-foreground">Top likely sources</p>
            <ul className="space-y-1 text-body text-foreground">
              {topThree.map((h: { hypothesis_id: string; name: string }) => (
                <li key={h.hypothesis_id}>{h.name}</li>
              ))}
            </ul>
          </div>
        ) : null}
        <Link href="/saas-revenue-leakage-calculator/start">
          <Button className="min-h-[44px]">Run your own assessment</Button>
        </Link>
      </HairlineCard>
    </div>
  );
}
