"use client";

import { QueryClientProvider } from "@tanstack/react-query";
import { Toaster } from "sonner";

import { AuditSessionLifecycle } from "@/components/audit/audit-session-lifecycle";
import { FeedbackFab } from "@/components/feedback/feedback-fab";
import { AnalyticsProviderWrapper } from "@/components/providers/analytics-provider-wrapper";
import { getQueryClient } from "@/lib/query/query-client";

const queryClient = getQueryClient();

export function AppProviders({ children }: { children: React.ReactNode }) {
  return (
    <QueryClientProvider client={queryClient}>
      <AnalyticsProviderWrapper>
        <AuditSessionLifecycle />
        {children}
        <FeedbackFab />
        <Toaster position="top-right" richColors closeButton duration={4000} />
      </AnalyticsProviderWrapper>
    </QueryClientProvider>
  );
}
