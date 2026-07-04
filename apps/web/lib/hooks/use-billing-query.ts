"use client";

import { useQuery } from "@tanstack/react-query";

import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { getBilling } from "@/lib/report-api";

export function useBillingQuery(enabled = true) {
  const { getToken, isSignedIn, isLoaded } = useAppAuth();

  return useQuery({
    queryKey: queryKeys.billing,
    queryFn: async () => {
      const token = await getToken();
      if (!token) {
        throw new ApiError("Authentication required.", 401);
      }
      return getBilling(token);
    },
    enabled: enabled && isLoaded && isSignedIn,
  });
}
