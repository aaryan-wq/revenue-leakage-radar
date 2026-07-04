"use client";

import { Suspense } from "react";

import { AnalyticsProvider } from "@/components/providers/analytics-provider";

export function AnalyticsProviderWrapper({ children }: { children: React.ReactNode }) {
  return (
    <Suspense fallback={children}>
      <AnalyticsProvider>{children}</AnalyticsProvider>
    </Suspense>
  );
}
