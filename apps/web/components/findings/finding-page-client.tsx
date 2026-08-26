"use client";

import { useCallback, useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";

import { FindingDetailView } from "@/components/findings/finding-detail-view";
import { Button } from "@/components/ui/button";
import { PageShell } from "@/components/ui/page-loading";
import { getStoredAuditSession } from "@/lib/audit-session";
import { getFinding } from "@/lib/report-api";
import { useTrackOnce } from "@/lib/analytics/hooks";
import { AnalyticsEvents, type FindingDetailResponse } from "@rlr/shared";

export function FindingPageClient() {
  const params = useParams<{ id: string }>();
  const { getToken, isSignedIn } = useAppAuth();
  const [finding, setFinding] = useState<FindingDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const loadFinding = useCallback(async () => {
    const session = getStoredAuditSession();
    const authToken = isSignedIn ? await getToken() : null;

    try {
      const data = await getFinding(params.id, {
        auditSession: session?.sessionToken,
        authToken,
      });
      setFinding(data);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load finding.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn, params.id]);

  useEffect(() => {
    void loadFinding();
  }, [loadFinding]);

  useTrackOnce(
    AnalyticsEvents.REMEDIATION_VIEWED,
    finding?.recommendation
      ? {
          audit_id: finding.audit_id,
          finding_id: finding.id,
        }
      : undefined,
    Boolean(finding?.recommendation),
  );

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Unable to copy link.");
    }
  };

  if (!isLoading && error && !finding) {
    return (
      <div className="mx-auto max-w-report px-6 py-20 text-center md:px-10">
        <p className="text-lg text-muted-foreground">{error}</p>
        <Button className="mt-6" onClick={() => void loadFinding()}>
          Retry
        </Button>
      </div>
    );
  }

  return (
    <PageShell isLoading={isLoading} message="Loading finding details…" variant="detail">
      {finding && (
        <FindingDetailView
          finding={finding}
          mode="live"
          copied={copied}
          onCopyLink={handleCopyLink}
        />
      )}
    </PageShell>
  );
}
