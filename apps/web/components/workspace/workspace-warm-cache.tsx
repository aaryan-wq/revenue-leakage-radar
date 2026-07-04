"use client";

import { useDashboardQuery } from "@/lib/hooks/use-dashboard-query";

/** Prefetch workspace data as soon as the user enters the workspace shell. */
export function WorkspaceWarmCache() {
  useDashboardQuery();
  return null;
}
