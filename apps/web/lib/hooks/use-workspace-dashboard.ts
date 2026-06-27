"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { getDashboard } from "@/lib/report-api";
import type { DashboardResponse } from "@rlr/shared";

export function useWorkspaceDashboard() {
  const router = useRouter();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    if (!isSignedIn) return;
    setIsLoading(true);
    try {
      const token = await getToken();
      if (!token) {
        setError("Authentication required.");
        return;
      }
      const data = await getDashboard(token);
      setDashboard(data);
      setError(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to load workspace data. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/dashboard");
      return;
    }
    void loadDashboard();
  }, [isLoaded, isSignedIn, loadDashboard, router]);

  return { dashboard, isLoading: !isLoaded || isLoading, error, reload: loadDashboard, isSignedIn, isLoaded };
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
