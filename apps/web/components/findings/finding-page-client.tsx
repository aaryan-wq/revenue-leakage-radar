"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { Check, Copy, Link2 } from "lucide-react";

import { SeverityBadge } from "@/components/findings/severity-badge";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getStoredAuditSession } from "@/lib/audit-session";
import { getFinding } from "@/lib/report-api";
import { formatCurrency, type FindingDetailResponse } from "@rlr/shared";

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

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      setError("Unable to copy link.");
    }
  };

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading finding details…" />;
  }

  if (error && !finding) {
    return (
      <GlassCard padding="md" className="border-error/20 bg-error-bg text-center">
        <p className="text-body text-gray-700">{error}</p>
        <Button className="mt-6" onClick={() => void loadFinding()}>
          Retry
        </Button>
      </GlassCard>
    );
  }

  if (!finding) return null;

  return (
    <div className="space-y-12">
      <GlassCard padding="lg" elevated>
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <div className="flex flex-wrap items-center gap-3">
              <SeverityBadge severity={finding.severity} />
              <span className="text-small text-gray-500">{finding.category_label}</span>
            </div>
            <h1 className="mt-4 text-h2 font-semibold text-gray-900">{finding.title}</h1>
            <p className="mt-2 text-caption text-gray-500">Rule: {finding.rule_id}</p>
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" size="sm" onClick={() => void handleCopyLink()}>
              {copied ? (
                <>
                  <Check className="mr-2 h-4 w-4" strokeWidth={1.75} />
                  Copied
                </>
              ) : (
                <>
                  <Copy className="mr-2 h-4 w-4" strokeWidth={1.75} />
                  Copy Link
                </>
              )}
            </Button>
            {finding.report_id && (
              <Link href={`/report/${finding.report_id}`}>
                <Button variant="ghost" size="sm">
                  <Link2 className="mr-2 h-4 w-4" strokeWidth={1.75} />
                  View Report
                </Button>
              </Link>
            )}
          </div>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="Estimated ARR" value={formatCurrency(finding.estimated_arr_loss)} />
          <Metric label="Monthly Impact" value={formatCurrency(finding.estimated_monthly_loss)} />
          <Metric label="Confidence" value={`${finding.confidence}%`} />
          <Metric label="Customer ID" value={finding.customer_id ?? "—"} />
        </div>

        {finding.recommendation && (
          <div className="mt-10 max-w-reading">
            <p className="text-overline uppercase text-gray-500">Recommendation</p>
            <p className="mt-2 text-body text-gray-700">{finding.recommendation}</p>
          </div>
        )}
      </GlassCard>

      <GlassCard padding="md">
        <h2 className="text-h3 font-semibold text-gray-900">Evidence</h2>
        {finding.evidence_records.length > 0 ? (
          <div className="mt-6 overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-small">
              <thead>
                <tr className="border-b border-border text-caption text-gray-500">
                  <th className="pb-3 pr-4 font-medium">Field</th>
                  <th className="pb-3 pr-4 font-medium">Expected</th>
                  <th className="pb-3 pr-4 font-medium">Actual</th>
                  <th className="pb-3 font-medium">References</th>
                </tr>
              </thead>
              <tbody>
                {finding.evidence_records.map((record, index) => (
                  <tr key={index} className="border-b border-border">
                    <td className="py-3 pr-4 text-gray-900">{record.field}</td>
                    <td className="py-3 pr-4 tabular-nums text-gray-700">{record.expected ?? "—"}</td>
                    <td className="py-3 pr-4 tabular-nums text-gray-700">{record.actual ?? "—"}</td>
                    <td className="py-3 text-caption text-gray-500">
                      {record.reference_ids
                        ? Object.entries(record.reference_ids)
                            .map(([k, v]) => `${k}: ${v}`)
                            .join(", ")
                        : "—"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="mt-4 text-body text-gray-500">No detailed evidence records.</p>
        )}
      </GlassCard>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="glass-subtle rounded-card p-5">
      <p className="text-caption text-gray-500">{label}</p>
      <p className="mt-2 text-h4 font-semibold tabular-nums text-gray-900">{value}</p>
    </div>
  );
}
