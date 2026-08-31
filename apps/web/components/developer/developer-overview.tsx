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

function formatRevenue(cents: number): string {
  return formatCurrency(String(cents / 100));
}

function MetricGrid({ metrics }: { metrics: Array<{ label: string; value: string }> }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((metric) => (
        <GlassCard key={metric.label} className="p-6">
          <p className="text-sm text-muted-foreground">{metric.label}</p>
          <p className="mt-3 font-heading text-2xl tabular-nums tracking-tight">{metric.value}</p>
        </GlassCard>
      ))}
    </div>
  );
}

function Section({ title, description, children }: { title: string; description?: string; children: React.ReactNode }) {
  return (
    <section className="space-y-4">
      <div>
        <h2 className="font-heading text-xl tracking-tight">{title}</h2>
        {description && <p className="mt-1 text-sm text-muted-foreground">{description}</p>}
      </div>
      {children}
    </section>
  );
}

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

  return (
    <div className="space-y-10">
      <Section title="Audits and reports" description="Verification pipeline and report outcomes.">
        <MetricGrid
          metrics={[
            { label: "Total audits", value: data.total_audits.toLocaleString() },
            { label: "Completed audits", value: data.completed_audits.toLocaleString() },
            { label: "In progress", value: data.audits_in_progress.toLocaleString() },
            { label: "Anonymous audits", value: data.anonymous_audits.toLocaleString() },
            { label: "Linked users", value: data.linked_users.toLocaleString() },
            { label: "Reports generated", value: data.total_reports.toLocaleString() },
            { label: "Purchased reports", value: data.purchased_reports.toLocaleString() },
            { label: "Purchase conversion", value: `${data.purchase_conversion_pct}%` },
            {
              label: "Recoverable ARR (all reports)",
              value: formatCurrency(data.total_recoverable_arr),
            },
            {
              label: "Average recoverable ARR",
              value: formatCurrency(data.average_recoverable_arr),
            },
            { label: "Audits (7 days)", value: data.audits_last_7_days.toLocaleString() },
            { label: "Audits (30 days)", value: data.audits_last_30_days.toLocaleString() },
          ]}
        />
      </Section>

      <Section title="Revenue and memberships" description="Checkout activity and active plans.">
        <MetricGrid
          metrics={[
            { label: "Total purchases", value: data.total_purchases.toLocaleString() },
            { label: "Purchases (7 days)", value: data.purchases_last_7_days.toLocaleString() },
            { label: "Purchases (30 days)", value: data.purchases_last_30_days.toLocaleString() },
            { label: "Refunded purchases", value: data.refunded_purchases.toLocaleString() },
            {
              label: "Purchase revenue",
              value: formatRevenue(data.total_purchase_revenue_cents),
            },
            { label: "Active memberships", value: data.active_memberships.toLocaleString() },
            { label: "Companies", value: data.total_companies.toLocaleString() },
          ]}
        />
      </Section>

      <Section
        title="Calculator assessments"
        description="SaaS revenue leakage calculator funnel and lead capture."
      >
        <MetricGrid
          metrics={[
            { label: "Total assessments", value: data.total_assessments.toLocaleString() },
            { label: "Completed assessments", value: data.completed_assessments.toLocaleString() },
            { label: "Assessments (7 days)", value: data.assessments_last_7_days.toLocaleString() },
            { label: "Assessments (30 days)", value: data.assessments_last_30_days.toLocaleString() },
            { label: "Leads captured", value: data.assessments_with_leads.toLocaleString() },
            { label: "Scan intent leads", value: data.assessments_scan_intent.toLocaleString() },
            {
              label: "Linked to audits",
              value: data.assessments_linked_to_audits.toLocaleString(),
            },
            {
              label: "Assessment to audit conversion",
              value: `${data.assessment_to_audit_conversion_pct}%`,
            },
          ]}
        />
      </Section>

      <GlassCard className="p-8">
        <h2 className="font-heading text-xl tracking-tight">Quick actions</h2>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link href="/developer/audits" className={buttonVariants({ variant: "secondary" })}>
            Search audits
          </Link>
          <Link href="/developer/reports" className={buttonVariants({ variant: "secondary" })}>
            Search reports
          </Link>
          <Link href="/developer/assessments" className={buttonVariants({ variant: "secondary" })}>
            Calculator assessments
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
