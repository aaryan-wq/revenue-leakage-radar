"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { fetchShare } from "@/lib/estimator/api";
import { formatCurrency } from "@rlr/shared";

export function EstimatorShareClient({ token }: { token: string }) {
  const [data, setData] = useState<Awaited<ReturnType<typeof fetchShare>> | null>(null);

  useEffect(() => {
    void fetchShare(token).then(setData);
  }, [token]);

  if (!data) return <PageLoadingSkeleton message="Loading shared estimate…" />;

  return (
    <div className="mx-auto max-w-readable px-6 py-16 md:px-10">
      <HairlineCard padding="lg" className="space-y-4">
        <p className="text-overline text-destructive">{data.disclaimer}</p>
        <h1 className="text-h2">SaaS Revenue Leakage Assessment</h1>
        <p className="text-metric-xl tabular-nums">
          {formatCurrency(data.estimate.low)} to {formatCurrency(data.estimate.high)} ARR
        </p>
        <p className="text-body text-muted-foreground">Confidence: {data.confidence}</p>
        <ul className="list-disc pl-5 text-body text-muted-foreground">
          {data.top_hypotheses.map((h: { hypothesis_id: string; name: string }) => (
            <li key={h.hypothesis_id}>{h.name}</li>
          ))}
        </ul>
        <Link href="/saas-revenue-leakage-calculator" className="text-small underline">
          Run your own assessment
        </Link>
      </HairlineCard>
    </div>
  );
}
