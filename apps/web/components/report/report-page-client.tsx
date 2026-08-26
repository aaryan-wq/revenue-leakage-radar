"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";

import { FindingDetailView } from "@/components/findings/finding-detail-view";
import { FreeSummaryView } from "@/components/summary/free-summary-view";
import { ReportView } from "@/components/report/report-view";
import { Button } from "@/components/ui/button";
import { PageShell } from "@/components/ui/page-loading";
import { getStoredAuditSession } from "@/lib/audit-session";
import { useReportQuery } from "@/lib/hooks/use-report-query";
import { ApiError } from "@/lib/api";
import {
  devUnlockReport,
  downloadReportCsv,
  downloadReportEvidenceCsv,
  downloadReportPdf,
  getReportFreeSummary,
} from "@/lib/report-api";
import { toast } from "@/lib/toast";
import type { FreeSummaryResponse } from "@rlr/shared";

type ReportPageClientProps = {
  backHref?: string;
  backLabel?: string;
};

export function ReportPageClient({
  backHref = "/summary",
  backLabel = "Back to Summary",
}: ReportPageClientProps = {}) {
  const params = useParams<{ id: string }>();
  const { getToken, isSignedIn } = useAppAuth();
  const reportQuery = useReportQuery(params.id);
  const report = reportQuery.data ?? null;
  const isLoading = reportQuery.isLoading && !report;
  const error =
    reportQuery.error instanceof ApiError
      ? reportQuery.error.message
      : reportQuery.error instanceof Error
        ? reportQuery.error.message
        : null;
  const [isExporting, setIsExporting] = useState<"pdf" | "csv" | "evidence" | null>(null);
  const [isUnlocking, setIsUnlocking] = useState(false);
  const [freeSummary, setFreeSummary] = useState<FreeSummaryResponse | null>(null);
  const [isLoadingSummary, setIsLoadingSummary] = useState(false);

  const isLocked = Boolean(error?.toLowerCase().includes("purchased"));

  const loadFreeSummary = useCallback(async () => {
    if (!isSignedIn || !isLocked) return;
    setIsLoadingSummary(true);
    try {
      const token = await getToken();
      if (!token) return;
      const summary = await getReportFreeSummary(params.id, token);
      setFreeSummary(summary);
    } catch {
      setFreeSummary(null);
    } finally {
      setIsLoadingSummary(false);
    }
  }, [getToken, isLocked, isSignedIn, params.id]);

  useEffect(() => {
    if (isLocked && isSignedIn) {
      void loadFreeSummary();
    }
  }, [isLocked, isSignedIn, loadFreeSummary]);

  const handleExport = async (type: "pdf" | "csv" | "evidence") => {
    if (!report) return;
    setIsExporting(type);
    try {
      const session = getStoredAuditSession();
      const authToken = isSignedIn ? await getToken() : null;
      if (type === "pdf") {
        await downloadReportPdf(report.id, session, authToken);
        toast.success("PDF downloaded.");
      } else if (type === "csv") {
        await downloadReportCsv(report.id, session, authToken);
        toast.success("Findings CSV downloaded.");
      } else {
        await downloadReportEvidenceCsv(report.id, session, authToken);
        toast.success("Evidence CSV downloaded.");
      }
    } catch {
      toast.error("Export failed.");
    } finally {
      setIsExporting(null);
    }
  };

  const handleDevUnlock = async () => {
    setIsUnlocking(true);
    try {
      await devUnlockReport(params.id);
      await reportQuery.refetch();
    } catch {
      toast.error("Dev unlock failed.");
    } finally {
      setIsUnlocking(false);
    }
  };

  if (!isLoading && error && !report) {
    if (isLocked && (isLoadingSummary || freeSummary)) {
      return (
        <PageShell
          isLoading={isLoadingSummary}
          message="Loading free summary…"
          variant="report"
        >
          {freeSummary && (
            <FreeSummaryView
              summary={freeSummary}
              onUnlocked={() => {
                void loadFreeSummary();
                void reportQuery.refetch();
              }}
              footer={
                <div className="border-t border-line pt-10">
                  <Link
                    href={backHref}
                    className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                  >
                    ← {backLabel}
                  </Link>
                </div>
              }
            />
          )}
        </PageShell>
      );
    }

    return (
      <div className="mx-auto max-w-report px-6 py-20 text-center md:px-10">
        <p className="text-lg leading-relaxed text-muted-foreground">
          {isLocked
            ? "This report requires purchase before viewing detailed findings."
            : error}
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          {isLocked && (
            <>
              <Link href={backHref}>
                <Button variant="secondary">{backLabel}</Button>
              </Link>
              <Link href={`/pricing?report_id=${params.id}`}>
                <Button>View Pricing</Button>
              </Link>
              {process.env.NODE_ENV === "development" && (
                <Button
                  variant="ghost"
                  onClick={() => void handleDevUnlock()}
                  disabled={isUnlocking}
                >
                  {isUnlocking ? "Unlocking…" : "Dev Unlock"}
                </Button>
              )}
            </>
          )}
          {!isLocked && <Button onClick={() => void reportQuery.refetch()}>Retry</Button>}
        </div>
      </div>
    );
  }

  if (!isLoading && !report) return null;

  return (
    <PageShell isLoading={isLoading} message="Loading report…" variant="report">
      {report && (
        <ReportView
          report={report}
          mode="live"
          isSignedIn={isSignedIn}
          isExporting={isExporting}
          onExport={handleExport}
          backHref={backHref}
          backLabel={backLabel}
        />
      )}
    </PageShell>
  );
}
