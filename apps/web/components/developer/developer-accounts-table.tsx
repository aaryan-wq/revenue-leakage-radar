"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { getAdminAccounts } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import type { AdminAccountListItem } from "@rlr/shared";

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

function formatPlan(plan: string | null): string {
  if (!plan || plan === "none") return "Free";
  return plan;
}

export function DeveloperAccountsTable() {
  const { getToken } = useAppAuth();
  const [search, setSearch] = useState("");
  const [query, setQuery] = useState("");
  const [page, setPage] = useState(1);

  const accountsQuery = useQuery({
    queryKey: queryKeys.adminAccounts({ q: query, page }),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminAccounts(token, {
        q: query || undefined,
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

  if (accountsQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading accounts…" variant="list" />;
  }

  if (accountsQuery.error) {
    const message =
      accountsQuery.error instanceof ApiError
        ? accountsQuery.error.message
        : "Unable to load accounts.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void accountsQuery.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = accountsQuery.data;
  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      <form onSubmit={handleSearch} className="flex flex-col gap-3 sm:flex-row">
        <input
          type="search"
          value={search}
          onChange={(event) => setSearch(event.target.value)}
          placeholder="Search by name, email, or Clerk user ID"
          className="h-11 flex-1 rounded-xl border border-line/60 bg-secondary/20 px-4 text-sm outline-none focus:border-primary/40 focus:ring-2 focus:ring-primary/20"
        />
        <Button type="submit">Search</Button>
      </form>

      <GlassCard className="overflow-hidden p-0">
        {items.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground">No accounts match your search.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-line/60 bg-secondary/20 text-left">
                <tr>
                  <th className="px-6 py-4 font-medium">Account</th>
                  <th className="px-6 py-4 font-medium">Plan</th>
                  <th className="px-6 py-4 font-medium text-right">Audits</th>
                  <th className="px-6 py-4 font-medium text-right">Purchases</th>
                  <th className="px-6 py-4 font-medium text-right">Reports left</th>
                  <th className="px-6 py-4 font-medium">Joined</th>
                  <th className="px-6 py-4 font-medium">Last active</th>
                </tr>
              </thead>
              <tbody>
                {items.map((account: AdminAccountListItem) => (
                  <tr
                    key={account.clerk_user_id}
                    className="border-b border-line/40 last:border-0 align-top"
                  >
                    <td className="px-6 py-4">
                      <div className="font-medium">
                        {account.clerk_user_name ?? "Unknown user"}
                      </div>
                      <div className="mt-1 space-y-0.5 text-xs text-muted-foreground">
                        {account.clerk_user_email && <div>{account.clerk_user_email}</div>}
                        <div>{account.clerk_user_id}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="gray">{formatPlan(account.plan)}</Badge>
                      {account.membership_status && account.membership_status !== "active" && (
                        <div className="mt-2 text-xs text-muted-foreground">
                          {account.membership_status}
                        </div>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums">{account.audit_count}</td>
                    <td className="px-6 py-4 text-right tabular-nums">{account.purchase_count}</td>
                    <td className="px-6 py-4 text-right tabular-nums">
                      {account.reports_remaining ?? "—"}
                    </td>
                    <td className="px-6 py-4 text-xs tabular-nums">
                      {formatTimestamp(account.joined_at)}
                    </td>
                    <td className="px-6 py-4 text-xs tabular-nums">
                      {formatTimestamp(account.last_active_at)}
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
