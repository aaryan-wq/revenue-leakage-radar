"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { getAdminAssessments } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { formatCurrency, type AdminAssessmentListItem } from "@rlr/shared";

function formatArr(amount: string | null, currency: string | null): string {
  if (!amount) return "—";
  const formatted = formatCurrency(amount);
  return currency ? `${formatted} ${currency}` : formatted;
}

function formatTimestamp(value: string | null): string {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function DeveloperAssessmentsTable() {
  const router = useRouter();
  const { getToken } = useAppAuth();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [statusFilter, setStatusFilter] = useState<"all" | "completed" | "started">("all");
  const [page, setPage] = useState(1);

  const statusParam = statusFilter === "all" ? undefined : statusFilter;

  const assessmentsQuery = useQuery({
    queryKey: queryKeys.adminAssessments({ q: query, status: statusParam, page }),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminAssessments(token, {
        q: query || undefined,
        status: statusParam,
        page,
        page_size: 25,
      });
    },
  });

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    setPage(1);
    setQuery(search.trim());
  };

  if (assessmentsQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading calculator assessments…" variant="list" />;
  }

  if (assessmentsQuery.error) {
    const message =
      assessmentsQuery.error instanceof ApiError
        ? assessmentsQuery.error.message
        : "Unable to load assessments.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void assessmentsQuery.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = assessmentsQuery.data;
  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="flex flex-col gap-3 lg:flex-row">
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by lead email, company, industry, or assessment ID"
          className="h-11 flex-1 rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/20"
        />
        <select
          value={statusFilter}
          onChange={(event) => {
            setStatusFilter(event.target.value as typeof statusFilter);
            setPage(1);
          }}
          className="h-11 rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm"
        >
          <option value="all">All statuses</option>
          <option value="completed">Completed</option>
          <option value="started">Started</option>
        </select>
        <Button type="submit">Search</Button>
      </form>

      <GlassCard className="overflow-hidden p-0">
        {items.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground">
            No calculator assessments match your search.
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-line/60 bg-secondary/20 text-left">
                <tr>
                  <th className="px-6 py-4 font-medium">Lead / company</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium">Completed</th>
                  <th className="px-6 py-4 font-medium text-right">Recoverable</th>
                  <th className="px-6 py-4 font-medium text-right">ARR</th>
                  <th className="px-6 py-4 font-medium">User</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((assessment: AdminAssessmentListItem) => (
                  <tr
                    key={assessment.assessment_id}
                    className="cursor-pointer border-b border-line/40 align-top transition-colors last:border-0 hover:bg-secondary/20"
                    onClick={() => router.push(`/developer/assessments/${assessment.assessment_id}`)}
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium">
                        {assessment.lead_company_name ??
                          assessment.lead_email ??
                          assessment.industry ??
                          "Anonymous lead"}
                      </div>
                      <div className="mt-1 space-y-0.5 text-xs text-muted-foreground">
                        {assessment.lead_email && <div>{assessment.lead_email}</div>}
                        {assessment.lead_role && <div>{assessment.lead_role}</div>}
                        <div>{assessment.assessment_id}</div>
                      </div>
                      <div className="mt-2 flex flex-wrap gap-2">
                        {assessment.scan_intent && (
                          <Badge variant="elevated">Scan intent</Badge>
                        )}
                        {assessment.lead_score != null && assessment.lead_score > 0 && (
                          <Badge variant="gray">Score {assessment.lead_score}</Badge>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="gray">{assessment.status}</Badge>
                      {assessment.industry && (
                        <div className="mt-2 text-xs text-muted-foreground">{assessment.industry}</div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {assessment.completed_at ? (
                        <span className="tabular-nums">{formatTimestamp(assessment.completed_at)}</span>
                      ) : assessment.started_at ? (
                        <>
                          <span className="tabular-nums text-muted-foreground">
                            {formatTimestamp(assessment.started_at)}
                          </span>
                          <div className="mt-1 text-muted-foreground">In progress</div>
                        </>
                      ) : (
                        <span className="text-muted-foreground">—</span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums">
                      {assessment.estimated_leakage
                        ? formatCurrency(assessment.estimated_leakage)
                        : "—"}
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums">
                      {formatArr(assessment.arr_amount, assessment.arr_currency)}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {assessment.clerk_user_id ? (
                        <>
                          <div className="font-medium text-foreground">
                            {assessment.clerk_user_name ?? "Unknown user"}
                          </div>
                          <div className="mt-1 text-muted-foreground">
                            {assessment.clerk_user_email ?? assessment.clerk_user_id}
                          </div>
                        </>
                      ) : (
                        <span className="text-muted-foreground">Not linked</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2" onClick={(event) => event.stopPropagation()}>
                        <Link
                          href={`/developer/assessments/${assessment.assessment_id}`}
                          className={buttonVariants({ variant: "ghost", size: "sm" })}
                        >
                          View
                        </Link>
                        {assessment.linked_audit_id && (
                          <Link
                            href={`/developer/audits/${assessment.linked_audit_id}`}
                            className={buttonVariants({ variant: "ghost", size: "sm" })}
                          >
                            Audit
                          </Link>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </GlassCard>

      {data && data.total > data.page_size && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-muted-foreground">
            Page {data.page} of {Math.ceil(data.total / data.page_size)}
          </p>
          <div className="flex gap-2">
            <Button
              variant="secondary"
              size="sm"
              disabled={page <= 1}
              onClick={() => setPage((current) => current - 1)}
            >
              Previous
            </Button>
            <Button
              variant="secondary"
              size="sm"
              disabled={page * data.page_size >= data.total}
              onClick={() => setPage((current) => current + 1)}
            >
              Next
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
