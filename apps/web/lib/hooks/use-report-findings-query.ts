"use client";

import { useInfiniteQuery } from "@tanstack/react-query";

import { useAppAuth } from "@/lib/app-auth";
import { getStoredAuditSession } from "@/lib/audit-session";
import { queryKeys } from "@/lib/query/keys";
import { getReportFindings, type ReportFindingsQuery } from "@/lib/report-api";

export function useReportFindingsQuery(
  reportId: string | null | undefined,
  query: ReportFindingsQuery = {},
) {
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const pageSize = query.page_size ?? 25;
  const sort = query.sort ?? "arr_desc";
  const category = query.category;

  return useInfiniteQuery({
    queryKey: reportId
      ? queryKeys.reportFindings(reportId, { pageSize, sort, category })
      : ["report-findings", "none"],
    queryFn: async ({ pageParam }) => {
      if (!reportId) {
        throw new Error("Report id required.");
      }
      const session = getStoredAuditSession();
      const authToken = isSignedIn ? await getToken() : null;
      return getReportFindings(
        reportId,
        {
          auditSession: session?.sessionToken,
          authToken,
        },
        {
          page: pageParam,
          page_size: pageSize,
          sort,
          category,
        },
      );
    },
    initialPageParam: 1,
    getNextPageParam: (lastPage) => (lastPage.has_more ? lastPage.page + 1 : undefined),
    enabled: Boolean(reportId) && isLoaded,
    staleTime: 120_000,
  });
}
