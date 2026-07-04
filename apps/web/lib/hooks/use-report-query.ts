"use client";

import { useQuery } from "@tanstack/react-query";

import { useAppAuth } from "@/lib/app-auth";
import { getStoredAuditSession } from "@/lib/audit-session";
import { queryKeys } from "@/lib/query/keys";
import { getReport } from "@/lib/report-api";

export function useReportQuery(reportId: string | null | undefined) {
  const { getToken, isSignedIn, isLoaded } = useAppAuth();

  return useQuery({
    queryKey: reportId ? queryKeys.report(reportId) : ["report", "none"],
    queryFn: async () => {
      if (!reportId) {
        throw new Error("Report id required.");
      }
      const session = getStoredAuditSession();
      const authToken = isSignedIn ? await getToken() : null;
      return getReport(reportId, {
        auditSession: session?.sessionToken,
        authToken,
      });
    },
    enabled: Boolean(reportId) && isLoaded,
    staleTime: 120_000,
  });
}
