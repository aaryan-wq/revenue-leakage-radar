"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { useQuery } from "@tanstack/react-query";

import { getAdminMe } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";

export function useAdminAccess(redirectOnDenied = true) {
  const router = useRouter();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();

  const query = useQuery({
    queryKey: queryKeys.adminMe,
    queryFn: async () => {
      const token = await getToken();
      if (!token) {
        throw new ApiError("Authentication required.", 401);
      }
      return getAdminMe(token);
    },
    enabled: isLoaded && isSignedIn,
    retry: false,
  });

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/developer");
      return;
    }
    if (!redirectOnDenied || query.isLoading || query.isFetching) return;
    if (query.error instanceof ApiError && query.error.status === 403) {
      router.replace("/dashboard");
    }
  }, [
    isLoaded,
    isSignedIn,
    query.error,
    query.isFetching,
    query.isLoading,
    redirectOnDenied,
    router,
  ]);

  const isAdmin = query.data?.is_admin === true;
  const isChecking = !isLoaded || query.isLoading;
  const accessDenied = query.error instanceof ApiError && query.error.status === 403;

  return {
    isAdmin,
    isChecking,
    accessDenied,
    adminEmail: query.data?.email ?? null,
    error: query.error,
    reload: query.refetch,
  };
}
