"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { Button, buttonVariants } from "@/components/ui/button";
import { getAdminOverview } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { formatCurrency } from "@rlr/shared";

export function DeveloperOverview() {
  const { getToken } = useAppAuth();
  const query = useQuery({
    queryKey: queryKeys.adminOverview,
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminOverview(token);
    },
  });

  if (query.isLoading) {
    return <PageLoadingSkeleton message="Loading platform metrics…" variant="dashboard" />;
  }

  if (query.error || !query.data) {
    const message =
      query.error instanceof ApiError ? query.error.message : "Unable to load overview.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void query.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = query.data;
  const metrics = [
    { label: "Total audits", value: data.total_audits.toLocaleString() },
    { label: "Linked users", value: data.linked_users.toLocaleString() },
    { label: "Reports generated", value: data.total_reports.toLocaleString() },
    { label: "Purchased reports", value: data.purchased_reports.toLocaleString() },
    { label: "Total purchases", value: data.total_purchases.toLocaleString() },
    {
      label: "Recoverable ARR (all reports)",
      value: formatCurrency(data.total_recoverable_arr),
    },
    { label: "Audits (7 days)", value: data.audits_last_7_days.toLocaleString() },
    { label: "Purchases (7 days)", value: data.purchases_last_7_days.toLocaleString() },
  ];

  return (
    <div className="space-y-8">
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <GlassCard key={metric.label} className="p-6">
            <p className="text-sm text-muted-foreground">{metric.label}</p>
            <p className="mt-3 font-heading text-2xl tabular-nums tracking-tight">{metric.value}</p>
          </GlassCard>
        ))}
      </div>

      <GlassCard className="p-8">
        <h2 className="font-heading text-xl tracking-tight">Quick actions</h2>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/developer/audits" className={buttonVariants({ variant: "secondary" })}>
            Search audits
          </Link>
          <Link href="/developer/reports" className={buttonVariants({ variant: "secondary" })}>
            Search reports
          </Link>
          <Link href="/developer/logs" className={buttonVariants({ variant: "secondary" })}>
            View operational logs
          </Link>
          <Link href="/developer/notes" className={buttonVariants({ variant: "secondary" })}>
            Support notes
          </Link>
        </div>
      </GlassCard>
    </div>
  );
}
