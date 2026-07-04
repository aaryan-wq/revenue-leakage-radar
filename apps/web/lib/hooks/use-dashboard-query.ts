"use client";

import { useQuery } from "@tanstack/react-query";

import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { getDashboard } from "@/lib/report-api";

export function useDashboardQuery(enabled = true) {
  const { getToken, isSignedIn, isLoaded } = useAppAuth();

  return useQuery({
    queryKey: queryKeys.dashboard,
    queryFn: async () => {
      const token = await getToken();
      if (!token) {
        throw new ApiError("Authentication required.", 401);
      }
      return getDashboard(token);
    },
    enabled: enabled && isLoaded && isSignedIn,
  });
}
