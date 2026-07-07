"use client";

import { useCallback, useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { Loader2 } from "lucide-react";

import { ColumnMappingTable } from "@/components/validation/column-mapping-table";
import { PlatformBadge } from "@/components/validation/platform-badge";
import { ValidationIssuesList } from "@/components/validation/validation-issues-list";
import { ValidationResultBanner } from "@/components/validation/validation-result-banner";
import { ValidationSkeleton } from "@/components/validation/validation-skeleton";
import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { ApiError } from "@/lib/api";
import {
  abandonAuditOnExit,
  clearAuditSession,
  getAuditStatus,
  getStoredAuditSession,
  getValidationReport,
  isProcessingStatus,
  isValidationSettled,
  pollValidationUntilSettled,
  startValidation,
} from "@/lib/audit-session";
import { toast } from "@/lib/toast";
import { useTrackOnce } from "@/lib/analytics/hooks";
import { AnalyticsEvents } from "@rlr/shared";
import {
  analysisNavigationLabel,
  canNavigateToAnalysis,
} from "@/lib/validation-navigation";
import type { AuditStatus, ValidationReportResponse } from "@rlr/shared";

function shouldTriggerValidation(status: AuditStatus): boolean {
  if (isProcessingStatus(status)) return false;
  if (
    status === "ready_for_scan" ||
    status === "scanning" ||
    status === "generating_report" ||
    status === "completed" ||
    status === "payment_pending"
  ) {
    return false;
  }
  return true;
}

function processingLabel(status: AuditStatus | null): string {
  switch (status) {
    case "mapping":
      return "Detecting platform and mapping columns…";
    case "validating":
      return "Validating billing and CRM data…";
    case "normalizing":
      return "Normalizing into canonical format…";
    case "uploading":
      return "Preparing uploaded files…";
    default:
      return "Starting validation…";
  }
}

const PAGE_SHELL = "mx-auto max-w-upload px-6 pt-16 pb-28 md:px-10 md:pt-24";

export function ValidationPageClient() {
  const router = useRouter();
  const [report, setReport] = useState<ValidationReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<AuditStatus | null>(null);

  const loadReport = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) return null;
    const data = await getValidationReport(session);
    setReport(data);
    setCurrentStatus(data.status);
    return data;
  }, []);

  const runValidationFlow = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) {
      router.replace("/upload");
      return;
    }

    const status = await getAuditStatus(session);
    if (!(status.has_billing_upload ?? status.required_files_present)) {
      router.replace("/upload");
      return;
    }

    setCurrentStatus(status.status);

    if (shouldTriggerValidation(status.status)) {
      try {
        await startValidation(session);
      } catch (err) {
        const alreadyDone =
          err instanceof ApiError &&
          (err.status === 400 || err.message.toLowerCase().includes("already"));
        if (!alreadyDone) {
          throw err;
        }
      }
    }

    if (!isValidationSettled(status.status)) {
      await pollValidationUntilSettled(session, (tick) => setCurrentStatus(tick.status));
    }

    await loadReport();
  }, [loadReport, router]);

  useTrackOnce(
    AnalyticsEvents.CSV_MAPPING_REVIEWED,
    report
      ? {
          audit_id: report.audit_id,
          validation_status: report.validation_result ?? undefined,
        }
      : undefined,
    Boolean(report && !isLoading),
  );

  useEffect(() => {
    async function run() {
      try {
        await runValidationFlow();
        const session = getStoredAuditSession();
        if (session) {
          const finalReport = await getValidationReport(session);
          if (finalReport.status === "ready_for_scan") {
            toast.success("Validation passed. Ready to scan.");
          } else if (
            finalReport.status === "validation_failed" ||
            finalReport.status === "processing_failed"
          ) {
            toast.error("Validation failed. Review issues below.");
          }
        }
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Unable to load validation results. Please try again.";
        setError(message);
        toast.error("Validation could not be completed.");
      } finally {
        setIsLoading(false);
      }
    }

    void run();
  }, [runValidationFlow]);

  const handleBackToUpload = useCallback(() => {
    const needsReset =
      Boolean(error) ||
      report?.status === "validation_failed" ||
      report?.status === "processing_failed";

    if (needsReset) {
      void abandonAuditOnExit();
    }
    router.push("/upload");
  }, [error, report?.status, router]);

  const handleRetry = async () => {
    const session = getStoredAuditSession();
    if (!session) return;

    setIsLoading(true);
    setError(null);
    setReport(null);

    try {
      await runValidationFlow();
    } catch (err) {
      const message =
        err instanceof ApiError
          ? err.message
          : "Validation failed to start. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  };

  const isProcessing =
    isLoading || (currentStatus !== null && !isValidationSettled(currentStatus));

  if (isProcessing && !error) {
    return (
      <section className={PAGE_SHELL}>
        <p className="mb-4 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Step two · Validate your data
        </p>
        <h1 className="max-w-2xl font-heading text-[clamp(2rem,4.5vw,2.8rem)] leading-[1.05] tracking-tight text-balance">
          Checking your files
        </h1>
        <p className="mt-4 text-sm text-muted-foreground">{processingLabel(currentStatus)}</p>
        <div className="mt-8 flex justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" strokeWidth={1.5} aria-hidden />
        </div>
        <div className="mt-10">
          <ValidationSkeleton />
        </div>
      </section>
    );
  }

  if (error) {
    return (
      <section className={PAGE_SHELL}>
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-sm text-foreground">{error}</p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            <Button onClick={() => void handleRetry()}>Retry Validation</Button>
            <Button
              variant="secondary"
              onClick={() => {
                clearAuditSession();
                router.push("/upload");
              }}
            >
              Start Over
            </Button>
          </div>
        </GlassCard>
      </section>
    );
  }

  if (!report) {
    return (
      <section className={PAGE_SHELL}>
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-sm text-muted-foreground">
            Validation results are not available yet.
          </p>
          <Button className="mt-6" onClick={() => void handleRetry()}>
            Retry
          </Button>
        </GlassCard>
      </section>
    );
  }

  const issues = report.validation_report?.issues ?? [];
  const blockingCount = report.summary?.blocking_count ?? 0;
  const warningCount = report.summary?.warning_count ?? 0;

  return (
    <section className={`${PAGE_SHELL} space-y-12`}>
      <Reveal>
        <p className="mb-4 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Step two · Validate your data
        </p>
        <h1 className="max-w-2xl font-heading text-[clamp(2rem,4.5vw,2.8rem)] leading-[1.05] tracking-tight text-balance">
          Validation results
        </h1>
        <p className="mt-4 max-w-xl text-sm leading-relaxed text-muted-foreground">
          We mapped your columns, ran schema checks, and normalized records into our canonical
          billing model before verification.
        </p>
      </Reveal>

      <Reveal delay={0.05}>
        <ValidationResultBanner
          result={report.validation_result}
          status={report.status}
          ingestionError={report.ingestion_error}
        />
      </Reveal>

      <Reveal delay={0.08}>
        <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-4">
          {[
            { label: "Blocking", value: String(blockingCount) },
            { label: "Warnings", value: String(warningCount) },
            { label: "Issues", value: String(report.summary?.issue_count ?? issues.length) },
            {
              label: "Ready to scan",
              value: canNavigateToAnalysis(report) ? "Yes" : "No",
            },
          ].map((stat) => (
            <div key={stat.label} className="bg-card px-5 py-5">
              <dt className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                {stat.label}
              </dt>
              <dd className="mt-2 font-heading text-2xl tracking-tight tnum">{stat.value}</dd>
            </div>
          ))}
        </dl>
      </Reveal>

      <Reveal delay={0.1}>
        <section className="border-t border-line pt-10">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <h2 className="font-heading text-2xl tracking-tight text-foreground">
              Platform detection
            </h2>
            <PlatformBadge platform={report.platform} />
          </div>
          {!report.platform && (
            <p className="mt-3 text-sm text-muted-foreground">
              No single billing platform signature detected. Using generic CSV mapping.
            </p>
          )}
        </section>
      </Reveal>

      <Reveal delay={0.12}>
        <section className="border-t border-line pt-10">
          <h2 className="font-heading text-2xl tracking-tight text-foreground">Column mapping</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            How source headers were interpreted for each uploaded file.
          </p>
          <div className="mt-6">
            <ColumnMappingTable mappings={report.column_mappings} />
          </div>
        </section>
      </Reveal>

      <Reveal delay={0.16}>
        <section className="border-t border-line pt-10">
          <h2 className="font-heading text-2xl tracking-tight text-foreground">Validation checks</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Blocking errors must be fixed before scanning. Warnings are informational.
          </p>
          <div className="mt-6">
            <ValidationIssuesList issues={issues} />
          </div>
        </section>
      </Reveal>

      <div className="flex flex-wrap items-center gap-4 border-t border-line pt-10">
        {canNavigateToAnalysis(report) && (
          <Button onClick={() => router.push("/analysis")}>
            {analysisNavigationLabel(report)}
          </Button>
        )}
        {report.status === "completed" && (
          <Button variant="secondary" onClick={() => router.push("/summary")}>
            View Summary
          </Button>
        )}
        <Button variant="secondary" onClick={handleBackToUpload}>
          Back to Upload
        </Button>
        {(report.status === "validation_failed" || report.status === "processing_failed") && (
          <Button variant="ghost" onClick={() => void handleRetry()}>
            Retry
          </Button>
        )}
      </div>
    </section>
  );
}
