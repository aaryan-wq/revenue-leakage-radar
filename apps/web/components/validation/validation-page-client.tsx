"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { ColumnMappingTable } from "@/components/validation/column-mapping-table";
import { PlatformBadge } from "@/components/validation/platform-badge";
import { ValidationIssuesList } from "@/components/validation/validation-issues-list";
import { ValidationResultBanner } from "@/components/validation/validation-result-banner";
import { ValidationSkeleton } from "@/components/validation/validation-skeleton";
import { Button } from "@/components/ui/button";
import {
  getAuditStatus,
  getStoredAuditSession,
  getValidationReport,
  isProcessingStatus,
  pollAuditUntil,
  startValidation,
} from "@/lib/audit-session";
import type { AuditStatus, ValidationReportResponse } from "@rlr/shared";

const TERMINAL_STATUSES: AuditStatus[] = [
  "ready_for_scan",
  "validation_failed",
  "processing_failed",
];

function isTerminal(status: AuditStatus): boolean {
  return TERMINAL_STATUSES.includes(status);
}

export function ValidationPageClient() {
  const router = useRouter();
  const [report, setReport] = useState<ValidationReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<AuditStatus | null>(null);

  const loadReport = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) return;
    const data = await getValidationReport(session);
    setReport(data);
    setCurrentStatus(data.status);
  }, []);

  useEffect(() => {
    async function run() {
      const session = getStoredAuditSession();
      if (!session) {
        router.replace("/upload");
        return;
      }

      try {
        let status = await getAuditStatus(session);
        if (!status.required_files_present) {
          router.replace("/upload");
          return;
        }

        setCurrentStatus(status.status);

        if (!isProcessingStatus(status.status) && !isTerminal(status.status)) {
          await startValidation(session);
        }

        await pollAuditUntil(
          session,
          (tick) => {
            setCurrentStatus(tick.status);
            return isProcessingStatus(tick.status);
          },
          (tick) => setCurrentStatus(tick.status),
        );

        await loadReport();
      } catch {
        setError("Unable to load validation results. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }

    void run();
  }, [loadReport, router]);

  const handleRetry = async () => {
    const session = getStoredAuditSession();
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      await startValidation(session);
      await pollAuditUntil(
        session,
        (tick) => {
          setCurrentStatus(tick.status);
          return isProcessingStatus(tick.status);
        },
        (tick) => setCurrentStatus(tick.status),
      );
      await loadReport();
    } catch {
      setError("Validation failed to start. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || (currentStatus && isProcessingStatus(currentStatus))) {
    return (
      <div>
        <div className="mb-8 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-gray-400" strokeWidth={1.75} />
          <p className="text-body text-gray-500">
            {currentStatus === "mapping" && "Detecting platform and mapping columns…"}
            {currentStatus === "validating" && "Validating billing data…"}
            {currentStatus === "normalizing" && "Normalizing into canonical format…"}
            {(!currentStatus || currentStatus === "uploading") && "Starting validation…"}
          </p>
        </div>
        <ValidationSkeleton />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-card border border-error/20 bg-error-bg p-8 text-center">
        <p className="text-body text-gray-700">{error}</p>
        <Button className="mt-6" onClick={() => void handleRetry()}>
          Retry Validation
        </Button>
      </div>
    );
  }

  if (!report) return null;

  const issues = report.validation_report?.issues ?? [];

  return (
    <div className="space-y-10">
      <ValidationResultBanner
        result={report.validation_result}
        status={report.status}
        ingestionError={report.ingestion_error}
      />

      <section className="rounded-card border border-gray-100 bg-white p-8 shadow-card">
        <div className="flex items-center justify-between">
          <h2 className="text-h3 text-gray-900">Platform Detection</h2>
          <PlatformBadge platform={report.platform} />
        </div>
      </section>

      <section className="rounded-card border border-gray-100 bg-white p-8 shadow-card">
        <h2 className="text-h3 text-gray-900">Column Mapping</h2>
        <div className="mt-6">
          <ColumnMappingTable mappings={report.column_mappings} />
        </div>
      </section>

      <section className="rounded-card border border-gray-100 bg-white p-8 shadow-card">
        <h2 className="text-h3 text-gray-900">Validation Checks</h2>
        <div className="mt-6">
          <ValidationIssuesList issues={issues} />
        </div>
      </section>

      <div className="flex flex-wrap items-center gap-4">
        {report.can_proceed_to_scan && (
          <Button onClick={() => router.push("/analysis")}>Start Scan</Button>
        )}
        <Link
          href="/upload"
          className="inline-flex h-12 items-center justify-center rounded-button border border-gray-200 bg-white px-6 text-body font-medium text-primary hover:border-gray-300"
        >
          Back to Upload
        </Link>
        {(report.status === "validation_failed" || report.status === "processing_failed") && (
          <Button variant="ghost" onClick={() => void handleRetry()}>
            Retry
          </Button>
        )}
      </div>
    </div>
  );
}
