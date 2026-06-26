"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { Download, FileSpreadsheet } from "lucide-react";

import { FindingsTable } from "@/components/report/findings-table";
import { OpportunityBreakdown } from "@/components/summary/opportunity-breakdown";
import { VerificationChecklist } from "@/components/summary/verification-checklist";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getStoredAuditSession } from "@/lib/audit-session";
import {
  devUnlockReport,
  downloadReportCsv,
  downloadReportEvidenceCsv,
  downloadReportPdf,
  getReport,
} from "@/lib/report-api";
import { toast } from "@/lib/toast";
import { formatCurrency, type ReportDetailResponse } from "@rlr/shared";

export function ReportPageClient() {
  const params = useParams<{ id: string }>();
  const { getToken, isSignedIn } = useAppAuth();
  const [report, setReport] = useState<ReportDetailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isExporting, setIsExporting] = useState<"pdf" | "csv" | "evidence" | null>(null);
  const [isUnlocking, setIsUnlocking] = useState(false);

  const loadReport = useCallback(async () => {
    const session = getStoredAuditSession();
    const authToken = isSignedIn ? await getToken() : null;

    try {
      const data = await getReport(params.id, {
        auditSession: session?.sessionToken,
        authToken,
      });
      setReport(data);
      setError(null);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Unable to load report.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn, params.id]);

  useEffect(() => {
    void loadReport();
  }, [loadReport]);

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
      setError("Export failed. Please try again.");
      toast.error("Export failed.");
    } finally {
      setIsExporting(null);
    }
  };

  const handleDevUnlock = async () => {
    setIsUnlocking(true);
    try {
      await devUnlockReport(params.id);
      await loadReport();
    } catch {
      setError("Dev unlock failed.");
    } finally {
      setIsUnlocking(false);
    }
  };

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading detailed report…" />;
  }

  if (error && !report) {
    const isLocked = error.toLowerCase().includes("purchased");
    return (
      <GlassCard padding="lg" elevated className="text-center">
        <p className="text-body text-gray-700">
          {isLocked
            ? "This report requires purchase before viewing detailed findings."
            : error}
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          {isLocked && (
            <>
              <Link href="/summary">
                <Button variant="secondary">Back to Summary</Button>
              </Link>
              <Link href={`/pricing?report_id=${params.id}`}>
                <Button>View Pricing</Button>
              </Link>
              {process.env.NODE_ENV === "development" && (
                <Button variant="ghost" onClick={() => void handleDevUnlock()} disabled={isUnlocking}>
                  {isUnlocking ? "Unlocking…" : "Dev Unlock"}
                </Button>
              )}
            </>
          )}
          {!isLocked && <Button onClick={() => void loadReport()}>Retry</Button>}
        </div>
      </GlassCard>
    );
  }

  if (!report) return null;

  const summary = report.executive_summary;

  return (
    <div className="space-y-16">
      <GlassCard padding="lg" elevated>
        <div className="flex flex-wrap items-start justify-between gap-6">
          <div>
            <p className="text-overline uppercase text-gray-500">
              Detailed Revenue Verification Report
            </p>
            {report.company_name && (
              <p className="mt-2 text-body text-gray-600">{report.company_name}</p>
            )}
            <h2 className="mt-4 text-metric-xl font-semibold tabular-nums text-gray-900">
              {formatCurrency(summary.recoverable_arr)}
            </h2>
            <p className="mt-2 text-body text-gray-600">Recoverable ARR</p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={() => void handleExport("pdf")}
              disabled={!report.purchased || isExporting !== null}
            >
              <Download className="mr-2 h-4 w-4" strokeWidth={1.75} />
              {isExporting === "pdf" ? "Downloading…" : "Download PDF"}
            </Button>
            <Button
              variant="secondary"
              onClick={() => void handleExport("csv")}
              disabled={!report.purchased || isExporting !== null}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" strokeWidth={1.75} />
              {isExporting === "csv" ? "Exporting…" : "Findings CSV"}
            </Button>
            <Button
              variant="secondary"
              onClick={() => void handleExport("evidence")}
              disabled={!report.purchased || isExporting !== null}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" strokeWidth={1.75} />
              {isExporting === "evidence" ? "Exporting…" : "Evidence CSV"}
            </Button>
          </div>
        </div>

        <div className="mt-10 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <Metric label="High Confidence ARR" value={formatCurrency(summary.high_confidence_arr)} />
          <Metric label="Medium Confidence ARR" value={formatCurrency(summary.medium_confidence_arr)} />
          <Metric label="Accounts" value={String(summary.accounts_reviewed)} />
          <Metric label="Invoices" value={String(summary.invoices_reviewed)} />
        </div>

        <div className="mt-10 max-w-reading">
          <h3 className="text-h3 font-semibold text-gray-900">Executive Summary</h3>
          <p className="mt-4 text-body leading-relaxed text-gray-700">{summary.narrative}</p>
        </div>
      </GlassCard>

      <OpportunityBreakdown items={report.opportunity_breakdown} />
      <VerificationChecklist checks={report.verification_checks} />
      <FindingsTable findings={report.findings} />

      <div className="flex gap-4">
        <Link href="/summary" className="text-small text-gray-500 underline-offset-4 hover:text-gray-900 hover:underline">
          ← Back to Summary
        </Link>
        {isSignedIn && (
          <Link href="/dashboard" className="text-small text-gray-500 underline-offset-4 hover:text-gray-900 hover:underline">
            Dashboard
          </Link>
        )}
      </div>
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
