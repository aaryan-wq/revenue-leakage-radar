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

  return (
    <div className="mx-auto max-w-readable px-6 py-16 md:px-10">
      <HairlineCard padding="lg" className="space-y-6 text-center">
        <p className="text-overline text-muted-foreground">Shared estimate</p>
        <h1 className="text-h2">Revenue leakage assessment</h1>
        <p className="text-metric-xl tabular-nums">
          {formatCurrency(data.estimate.low)} to {formatCurrency(data.estimate.high)}
        </p>
        <p className="text-caption text-muted-foreground">{data.disclaimer}</p>
        <ul className="space-y-2 text-body text-muted-foreground">
          {data.top_hypotheses.map((h: { hypothesis_id: string; name: string }) => (
            <li key={h.hypothesis_id}>{h.name}</li>
          ))}
        </ul>
        <Link href="/saas-revenue-leakage-calculator/start">
          <Button className="min-h-[44px]">Run your own assessment</Button>
        </Link>
      </HairlineCard>
    </div>
  );
}

