"use client";

import { useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { getAdminLogs } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import type { AdminLogEntry } from "@rlr/shared";

function formatTimestamp(value: string): string {
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

export function DeveloperLogsTable() {
  const { getToken } = useAppAuth();
  const [page, setPage] = useState(1);

  const logsQuery = useQuery({
    queryKey: queryKeys.adminLogs({ page }),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminLogs(token, { page, page_size: 50 });
    },
  });

  if (logsQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading operational logs…" variant="list" />;
  }

  if (logsQuery.error) {
    const message =
      logsQuery.error instanceof ApiError ? logsQuery.error.message : "Unable to load logs.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <Button className="mt-4" onClick={() => void logsQuery.refetch()}>
          Retry
        </Button>
      </div>
    );
  }

  const data = logsQuery.data;
  const items = data?.items ?? [];

  return (
    <div className="space-y-6">
      <GlassCard className="overflow-hidden p-0">
        {items.length === 0 ? (
          <div className="p-10 text-center text-muted-foreground">No operational logs yet.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full text-sm">
              <thead className="border-b border-line/60 bg-secondary/20 text-left">
                <tr>
                  <th className="px-6 py-4 font-medium">Timestamp</th>
                  <th className="px-6 py-4 font-medium">Type</th>
                  <th className="px-6 py-4 font-medium">Entity</th>
                  <th className="px-6 py-4 font-medium">Message</th>
                </tr>
              </thead>
              <tbody>
                {items.map((entry: AdminLogEntry) => (
                  <tr key={entry.id} className="border-b border-line/40 last:border-0 align-top">
                    <td className="px-6 py-4 whitespace-nowrap text-muted-foreground">
                      {formatTimestamp(entry.timestamp)}
                    </td>
                    <td className="px-6 py-4">
                      <Badge variant="gray">{entry.log_type}</Badge>
                    </td>
                    <td className="px-6 py-4 text-xs text-muted-foreground">
                      {entry.entity_type ?? "—"}
                      {entry.entity_id ? `: ${entry.entity_id}` : ""}
                    </td>
                    <td className="px-6 py-4 max-w-xl break-words">{entry.message}</td>
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
