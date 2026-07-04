"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { useDashboardQuery } from "@/lib/hooks/use-dashboard-query";
import type { DashboardResponse } from "@rlr/shared";

export function useWorkspaceDashboard() {
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAppAuth();
  const query = useDashboardQuery();

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/dashboard");
    }
  }, [isLoaded, isSignedIn, router]);

  const error =
    query.error instanceof ApiError
      ? query.error.message
      : query.error instanceof Error
        ? query.error.message
        : null;

  return {
    dashboard: (query.data ?? null) as DashboardResponse | null,
    isLoading: !isLoaded || (query.isLoading && !query.data),
    isFetching: query.isFetching,
    error,
    reload: () => query.refetch(),
    isSignedIn,
    isLoaded,
  };
}

export function sortAuditsByValue<T extends { purchased: boolean; recoverable_arr: string }>(
  audits: T[],
): T[] {
  return [...audits].sort((a, b) => {
    if (a.purchased !== b.purchased) return a.purchased ? -1 : 1;
    return parseFloat(b.recoverable_arr || "0") - parseFloat(a.recoverable_arr || "0");
  });
}

export function totalRecoverableArr(audits: { recoverable_arr: string }[]): number {
  return audits.reduce((sum, audit) => sum + Number.parseFloat(audit.recoverable_arr || "0"), 0);
}
