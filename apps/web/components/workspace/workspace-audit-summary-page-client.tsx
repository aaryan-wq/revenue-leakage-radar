"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter } from "next/navigation";

import { FreeSummaryView } from "@/components/summary/free-summary-view";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { DelayedPageFallback } from "@/components/ui/page-loading";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { getSummaryForAccount } from "@/lib/report-api";
import type { FreeSummaryResponse } from "@rlr/shared";

export function WorkspaceAuditSummaryPageClient() {
  const router = useRouter();
  const params = useParams<{ auditId: string }>();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [summary, setSummary] = useState<FreeSummaryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadSummary = useCallback(async () => {
    if (!isSignedIn) return;

    try {
      const token = await getToken();
      if (!token) {
        setError("Authentication required.");
        return;
      }
      const data = await getSummaryForAccount(params.auditId, token);
      setSummary(data);
      setError(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to load audit summary. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn, params.auditId]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace(`/sign-in?redirect_url=${encodeURIComponent(`/audits/${params.auditId}`)}`);
      return;
    }
    void loadSummary();
  }, [isLoaded, isSignedIn, loadSummary, params.auditId, router]);

  useEffect(() => {
    if (summary?.purchased) {
      router.replace(`/report/${summary.report_id}`);
    }
  }, [router, summary]);

  if (!isLoaded || isLoading) {
    return <DelayedPageFallback message="Loading audit summary…" variant="report" />;
  }

  if (error || !summary) {
    return (
      <div className="mx-auto max-w-report px-6 py-20 text-center md:px-10">
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-body text-foreground">{error ?? "Summary unavailable."}</p>
          <div className="mt-6 flex flex-wrap justify-center gap-4">
            <Button onClick={() => void loadSummary()}>Retry</Button>
            <Link href="/audits">
              <Button variant="secondary">Back to audits</Button>
            </Link>
          </div>
        </GlassCard>
      </div>
    );
  }

  if (summary.purchased) {
    return <DelayedPageFallback message="Opening report…" variant="report" />;
  }

  return (
    <FreeSummaryView
      summary={summary}
      onUnlocked={() => void loadSummary()}
      footer={
        <div className="border-t border-line pt-10">
          <Link
            href="/audits"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            ← Back to audits
          </Link>
        </div>
      }
    />
  );
}
