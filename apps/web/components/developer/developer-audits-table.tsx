"use client";

import Link from "next/link";
import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { adminReprocessAudit } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { getAdminAudits } from "@/lib/admin-api";
import { formatAuditStatusLabel } from "@/lib/format-audit-status";
import { formatCurrency, type AdminAuditListItem } from "@rlr/shared";
import { toast } from "@/lib/toast";

export function DeveloperAuditsTable() {
  const { getToken } = useAppAuth();
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);
  const [reprocessingId, setReprocessingId] = useState<string | null>(null);

  const auditsQuery = useQuery({
    queryKey: queryKeys.adminAudits({ q: query, page }),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminAudits(token, { q: query || undefined, page, page_size: 25 });
    },
  });

  const handleSearch = (event: React.FormEvent) => {
    event.preventDefault();
    setPage(1);
    setQuery(search.trim());
  };

  const handleReprocess = async (auditId: string) => {
    if (!window.confirm("Re-run verification for this audit?")) return;
    setReprocessingId(auditId);
    try {
      const token = await getToken();
      if (!token) return;
      await adminReprocessAudit(token, auditId);
      toast.success("Reprocess triggered.");
      await queryClient.invalidateQueries({ queryKey: ["admin", "audits"] });
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Reprocess failed.";
      toast.error(message);
    } finally {
      setReprocessingId(null);
    }
  };

  if (auditsQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading audits…" variant="list" />;
  }

  if (auditsQuery.error) {
    const message =
      auditsQuery.error instanceof ApiError ? auditsQuery.error.message : "Unable to load audits.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void auditsQuery.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = auditsQuery.data;
  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by company, user ID, audit ID, or status"
          className="h-11 flex-1 rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm outline-none ring-offset-background focus:border-primary/40 focus:ring-2 focus:ring-primary/20"
        />
        <Button type="submit">Search</Button>
      </form>

      <GlassCard className="overflow-hidden p-0">
        {items.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground">No audits match your search.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-line/60 bg-secondary/20 text-left">
                <tr>
                  <th className="px-6 py-4 font-medium">Company</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium text-right">Recoverable ARR</th>
                  <th className="px-6 py-4 font-medium">User</th>
                  <th className="px-6 py-4 font-medium text-right">Actions</th>
                </tr>
              </thead>
              <tbody>
                {items.map((audit: AdminAuditListItem) => (
                  <tr key={audit.audit_id} className="border-b border-line/40 last:border-0">
                    <td className="px-6 py-4">
                      <div className="font-medium">{audit.company_name ?? "Unknown company"}</div>
                      <div className="mt-1 text-xs text-muted-foreground">{audit.audit_id}</div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="gray">{formatAuditStatusLabel(audit.status)}</Badge>
                      {audit.purchased && (
                        <Badge className="ml-2" variant="elevated">
                          Purchased
                        </Badge>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums">
                      {audit.recoverable_arr ? formatCurrency(audit.recoverable_arr) : "—"}
                    </td>
                    <td className="px-6 py-4 text-xs">
                      {audit.clerk_user_id ? (
                        <>
                          <div className="font-medium text-foreground">
                            {audit.clerk_user_name ?? "Unknown user"}
                          </div>
                          <div className="mt-1 text-muted-foreground">
                            {audit.clerk_user_email ?? audit.clerk_user_id}
                          </div>
                        </>
                      ) : (
                        <span className="text-muted-foreground">Anonymous</span>
                      )}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
                        {audit.report_id && (
                          <Link
                            href={`/report/${audit.report_id}`}
                            className={buttonVariants({ variant: "ghost", size: "sm" })}
                          >
                            Report
                          </Link>
                        )}
                        <Button
                          size="sm"
                          variant="secondary"
                          disabled={reprocessingId === audit.audit_id}
                          onClick={() => void handleReprocess(audit.audit_id)}
                        >
                          Reprocess
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
