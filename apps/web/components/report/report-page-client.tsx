"use client";

import { useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { Download, FileSpreadsheet } from "lucide-react";

import { Logo } from "@/components/brand/logo";
import { CountUp } from "@/components/count-up";
import { CategoryBars } from "@/components/report/category-bars";
import { FindingsTable } from "@/components/report/findings-table";
import { Reveal } from "@/components/motion";
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
} from "@/lib/report-api";
import { toast } from "@/lib/toast";
import { formatCurrency, type ReportDetailResponse } from "@rlr/shared";

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
    const isLocked = error.toLowerCase().includes("purchased");
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
        <ReportContent
          report={report}
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

function ReportContent({
  report,
  isSignedIn,
  isExporting,
  onExport,
  backHref,
  backLabel,
}: {
  report: ReportDetailResponse;
  isSignedIn: boolean;
  isExporting: "pdf" | "csv" | "evidence" | null;
  onExport: (type: "pdf" | "csv" | "evidence") => void;
  backHref: string;
  backLabel: string;
}) {
  const summary = report.executive_summary;
  const recoverable = parseFloat(summary.recoverable_arr) || 0;
  const confidence = summary.confidence ? parseFloat(summary.confidence) : null;
  const periodLabel = report.generated_at
    ? new Date(report.generated_at).toLocaleDateString("en-US", {
        month: "short",
        year: "numeric",
      })
    : "Current period";

  return (
    <div className="min-h-screen">
      <section className="mx-auto max-w-report px-6 pt-16 pb-20 md:px-10 md:pt-24">
        <Reveal>
          <Logo variant="full" href={null} className="mb-10 h-12 sm:h-14" />
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            <span>Confidential</span>
            <span className="h-1 w-1 rounded-full bg-muted-foreground/50" />
            <span>{report.company_name ?? "Your organization"}</span>
            <span className="h-1 w-1 rounded-full bg-muted-foreground/50" />
            <span>{periodLabel}</span>
          </div>
          <h1 className="mt-8 max-w-3xl font-heading text-[clamp(2.4rem,6vw,4.4rem)] leading-[0.98] tracking-tight text-balance">
            Revenue Leakage Findings
          </h1>
          <p className="mt-7 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            An examination of billing, CRM, pricing, and subscription data, isolating
            recoverable revenue lost to verification failures over the reporting
            period.
          </p>
        </Reveal>

        <Reveal delay={0.15}>
          <div className="mt-16 grid items-end gap-10 border-t border-line pt-12 md:grid-cols-[1.3fr_1fr]">
            <div>
              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Total recoverable revenue
              </p>
              <div className="mt-4 font-heading text-[clamp(3rem,9vw,6rem)] leading-none tracking-tight tnum">
                <CountUp to={recoverable} prefix="$" duration={1.6} />
              </div>
              <p className="mt-5 max-w-md leading-relaxed text-muted-foreground">
                Identified across {summary.finding_count} distinct findings
                {confidence !== null
                  ? `, at a weighted confidence of ${Math.round(confidence)}%`
                  : ""}
                . The headline sums primary-attributed forward recoverable ARR only.
              </p>
              {summary.reconciliation && (
                <div className="mt-6 rounded-xl border border-line bg-secondary/20 px-5 py-4 text-sm leading-relaxed text-muted-foreground">
                  <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    ARR reconciliation
                  </p>
                  <p className="mt-2">
                    {summary.reconciliation.primary_findings} primary findings contribute{" "}
                    {formatCurrency(summary.reconciliation.primary_recoverable_arr)}.{" "}
                    {summary.reconciliation.secondary_findings > 0 && (
                      <>
                        {summary.reconciliation.secondary_findings} overlapping secondary
                        findings ({formatCurrency(summary.reconciliation.secondary_excluded_arr)})
                        are shown for evidence but excluded from totals.
                      </>
                    )}
                  </p>
                </div>
              )}
            </div>
            <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line">
              {[
                {
                  k: "Accounts",
                  v: String(summary.accounts_reviewed),
                },
                { k: "Findings", v: String(summary.finding_count) },
                {
                  k: "Confidence",
                  v: confidence !== null ? `${Math.round(confidence)}%` : "-",
                },
                {
                  k: "High confidence",
                  v: formatCurrency(summary.high_confidence_arr),
                },
              ].map((stat) => (
                <div key={stat.k} className="bg-card px-5 py-6">
                  <dt className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    {stat.k}
                  </dt>
                  <dd className="mt-2 font-heading text-2xl tracking-tight tnum">
                    {stat.v}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </Reveal>

        <Reveal delay={0.2}>
          <div className="mt-12 flex flex-wrap gap-3">
            <Button
              variant="secondary"
              onClick={() => void onExport("pdf")}
              disabled={!report.purchased || isExporting !== null}
            >
              <Download className="mr-2 h-4 w-4" strokeWidth={1.75} />
              {isExporting === "pdf" ? "Downloading…" : "Download PDF"}
            </Button>
            <Button
              variant="secondary"
              onClick={() => void onExport("csv")}
              disabled={!report.purchased || isExporting !== null}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" strokeWidth={1.75} />
              {isExporting === "csv" ? "Exporting…" : "Findings CSV"}
            </Button>
            <Button
              variant="secondary"
              onClick={() => void onExport("evidence")}
              disabled={!report.purchased || isExporting !== null}
            >
              <FileSpreadsheet className="mr-2 h-4 w-4" strokeWidth={1.75} />
              {isExporting === "evidence" ? "Exporting…" : "Evidence CSV"}
            </Button>
          </div>
        </Reveal>
      </section>

      {summary.narrative && (
        <section className="border-y border-line bg-secondary/30">
          <div className="mx-auto max-w-report px-6 py-20 md:px-10">
            <Reveal>
              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Executive summary
              </p>
              <p className="mt-6 max-w-reading text-lg leading-relaxed text-muted-foreground">
                {summary.narrative}
              </p>
            </Reveal>
          </div>
        </section>
      )}

      {report.opportunity_breakdown.length > 0 && (
        <section className="border-y border-line bg-secondary/30">
          <div className="mx-auto grid max-w-report gap-14 px-6 py-20 md:grid-cols-[0.9fr_1.1fr] md:px-10">
            <Reveal>
              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Where it leaks
              </p>
              <h2 className="mt-4 font-heading text-[clamp(1.7rem,3.5vw,2.6rem)] leading-[1.05] tracking-tight text-balance">
                Concentration of loss by revenue function.
              </h2>
              <p className="mt-5 leading-relaxed text-muted-foreground">
                Recoverable ARR grouped by verification category. Addressing the
                highest-impact categories first captures the majority of total
                recoverable revenue.
              </p>
            </Reveal>
            <Reveal delay={0.1}>
              <CategoryBars items={report.opportunity_breakdown} />
            </Reveal>
          </div>
        </section>
      )}

      <section className="mx-auto max-w-report px-6 py-24 md:px-10">
        <Reveal>
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            The findings
          </p>
          <h2 className="mt-4 max-w-xl font-heading text-[clamp(1.7rem,3.5vw,2.6rem)] leading-[1.05] tracking-tight text-balance">
            Each finding, ranked by recoverable impact.
          </h2>
        </Reveal>

        <div className="mt-16">
          <FindingsTable reportId={report.id} totalCount={report.findings_total} />
        </div>

        <Reveal>
          <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-10">
            <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
              Prepared by Paevo. Figures are estimates derived from
              the supplied data and intended for internal review.
            </p>
            <Link
              href="/dashboard"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
            >
              Open the workspace →
            </Link>
          </div>
        </Reveal>

        <div className="mt-8 flex flex-wrap gap-4">
          <Link
            href={backHref}
            className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
          >
            ← {backLabel}
          </Link>
          {isSignedIn && (
            <Link
              href="/dashboard"
              className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
            >
              Dashboard
            </Link>
          )}
        </div>
      </section>
    </div>
  );
}
