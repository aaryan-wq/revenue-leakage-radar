"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import {
  adminDeleteReport,
  adminRefundPurchase,
  adminUnlockReport,
  getAdminReports,
} from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { formatAuditStatusLabel } from "@/lib/format-audit-status";
import { formatCurrency, type AdminReportListItem } from "@rlr/shared";
import { toast } from "@/lib/toast";

export function DeveloperReportsTable() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [purchasedFilter, setPurchasedFilter] = useState<"all" | "purchased" | "unpurchased">(
    "all",
  );
  const [page, setPage] = useState(1);
  const [busyId, setBusyId] = useState<string | null>(null);

  const purchasedParam =
    purchasedFilter === "all" ? undefined : purchasedFilter === "purchased";

  const reportsQuery = useQuery({
    queryKey: queryKeys.adminReports({ q: query, purchased: purchasedParam, page }),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminReports(token, {
        q: query || undefined,
        purchased: purchasedParam,
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

  const invalidate = async () => {
    await queryClient.invalidateQueries({ queryKey: ["admin", "reports"] });
    await queryClient.invalidateQueries({ queryKey: queryKeys.adminOverview });
  };

  const handleUnlock = async (reportId: string) => {
    setBusyId(reportId);
    try {
      const token = await getToken();
      if (!token) return;
      await adminUnlockReport(token, reportId);
      toast.success("Report unlocked.");
      await invalidate();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Unlock failed.");
    } finally {
      setBusyId(null);
    }
  };

  const handleDelete = async (reportId: string) => {
    if (!window.confirm("Delete this report? This cannot be undone.")) return;
    setBusyId(reportId);
    try {
      const token = await getToken();
      if (!token) return;
      await adminDeleteReport(token, reportId);
      toast.success("Report deleted.");
      await invalidate();
    } catch (err) {
      toast.error(err instanceof ApiError ? err.message : "Delete failed.");
    } finally {
      setBusyId(null);
    }
  };

  if (reportsQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading reports…" variant="list" />;
  }

  if (reportsQuery.error) {
    const message =
      reportsQuery.error instanceof ApiError
        ? reportsQuery.error.message
        : "Unable to load reports.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void reportsQuery.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = reportsQuery.data;
  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="flex flex-col gap-3 lg:flex-row">
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by company, audit ID, report ID, or user"
          className="h-11 flex-1 rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/20"
        />
        <select
          value={purchasedFilter}
          onChange={(event) => {
            setPurchasedFilter(event.target.value as typeof purchasedFilter);
            setPage(1);
          }}
          className="h-11 rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm"
        >
          <option value="all">All reports</option>
          <option value="purchased">Purchased only</option>
          <option value="unpurchased">Unpurchased only</option>
        </select>
        <Button type="submit">Search</Button>
      </form>

      <GlassCard className="overflow-hidden p-0">
        {items.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground">No reports match your search.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-line/60 bg-secondary/20 text-left">
                <tr>
                  <th className="px-6 py-4 font-medium">Company</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium text-right">Recoverable ARR</th>
                  <th className="px-6 py-4 font-medium">Access</th>
                  <th className="px-6 py-4 font-medium">User</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((report: AdminReportListItem) => (
                  <tr key={report.report_id} className="border-b border-line/40 last:border-0">
                    <td className="px-6 py-4">
                      <div className="font-medium">{report.company_name ?? "Unknown company"}</div>
                      <div className="mt-1 text-xs text-muted-foreground">{report.report_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="gray">{formatAuditStatusLabel(report.status)}</Badge>
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums">
                      {formatCurrency(report.recoverable_arr)}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant={report.purchased ? "elevated" : "gray"}>
                        {report.purchased ? "Purchased" : "Locked"}
                      </Badge>
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {report.clerk_user_id ? (
                        <>
                          <div className="font-medium text-foreground">
                            {report.clerk_user_name ?? "Unknown user"}
                          </div>
                          <div className="mt-1 text-muted-foreground">
                            {report.clerk_user_email ?? report.clerk_user_id}
                          </div>
                        </>
                      ) : (
                        <span className="text-muted-foreground">Anonymous</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        <Link
                          href={`/report/${report.report_id}`}
                          className={buttonVariants({ variant: "ghost", size: "sm" })}
                        >
                          Open
                        </Link>
                        {!report.purchased && (
                          <Button
                            size="sm"
                            variant="secondary"
                            disabled={busyId === report.report_id}
                            onClick={() => void handleUnlock(report.report_id)}
                          >
                            Unlock
                          </Button>
                        )}
                        <Button
                          size="sm"
                          variant="ghost"
                          disabled={busyId === report.report_id}
                          onClick={() => void handleDelete(report.report_id)}
                        >
                          Delete
                        </Button>
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

// Exported for potential use from audit detail purchases; kept for future wiring.
export async function refundPurchaseWithPrompt(
  getToken: () => Promise<string | null>,
  purchaseId: string,
) {
  const reason = window.prompt("Refund reason (optional):") ?? undefined;
  if (!window.confirm("Process Stripe refund for this purchase?")) return;
  const token = await getToken();
  if (!token) return;
  await adminRefundPurchase(token, purchaseId, reason || undefined);
  toast.success("Refund processed.");
}
