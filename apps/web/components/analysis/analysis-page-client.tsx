"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Loader2 } from "lucide-react";

import { ScanPipeline } from "@/components/analysis/scan-pipeline";
import { ScanSkeleton } from "@/components/analysis/scan-skeleton";
import { Button } from "@/components/ui/button";
import {
  getScanReport,
  getStoredAuditSession,
  isScanProcessingStatus,
  pollScanUntil,
  startScan,
} from "@/lib/audit-session";
import type { AuditStatus, ScanReportResponse } from "@rlr/shared";

function formatArr(value: string): string {
  const num = Number.parseFloat(value);
  if (Number.isNaN(num)) return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(num);
}

export function AnalysisPageClient() {
  const router = useRouter();
  const [report, setReport] = useState<ScanReportResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentStatus, setCurrentStatus] = useState<AuditStatus | null>(null);

  const loadReport = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) return;
    const data = await getScanReport(session);
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
        let initial = await getScanReport(session);
        setCurrentStatus(initial.status);

        if (initial.status === "ready_for_scan") {
          await startScan(session);
        } else if (initial.status !== "completed" && !isScanProcessingStatus(initial.status)) {
          router.replace("/validation");
          return;
        }

        if (initial.status !== "completed") {
          initial = await pollScanUntil(
            session,
            (tick) => isScanProcessingStatus(tick.status),
            (tick) => {
              setCurrentStatus(tick.status);
              setReport(tick);
            },
          );
        }

        setReport(initial);
        setCurrentStatus(initial.status);
      } catch {
        setError("Unable to complete verification scan. Please try again.");
      } finally {
        setIsLoading(false);
      }
    }

    void run();
  }, [router]);

  const handleRetry = async () => {
    const session = getStoredAuditSession();
    if (!session) return;

    setIsLoading(true);
    setError(null);

    try {
      router.replace("/validation");
    } catch {
      setError("Unable to restart scan. Return to validation and try again.");
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading || (currentStatus && isScanProcessingStatus(currentStatus))) {
    return (
      <div>
        <div className="mb-8 flex items-center gap-3">
          <Loader2 className="h-5 w-5 animate-spin text-gray-400" strokeWidth={1.75} />
          <p className="text-body text-gray-500">
            {currentStatus === "scanning" && "Running deterministic verification checks…"}
            {currentStatus === "generating_report" && "Estimating recoverable revenue…"}
            {(!currentStatus || currentStatus === "ready_for_scan") && "Starting verification scan…"}
          </p>
        </div>
        <ScanSkeleton />
        {report && (
          <div className="mt-10">
            <ScanPipeline
              status={currentStatus ?? report.status}
              rulesCompleted={report.rules_completed}
              rulesTotal={report.rules_total}
            />
          </div>
        )}
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-card border border-error/20 bg-error-bg p-8 text-center">
        <p className="text-body text-gray-700">{error}</p>
        <Button className="mt-6" onClick={() => void handleRetry()}>
          Back to Validation
        </Button>
      </div>
    );
  }

  if (!report || report.status !== "completed") return null;

  return (
    <div className="space-y-10">
      <section className="rounded-card border border-success/20 bg-success-bg p-10 text-center shadow-card">
        <p className="text-caption font-medium uppercase tracking-wide text-success">Scan Complete</p>
        <h2 className="mt-4 text-h2 font-semibold text-gray-900 tabular-nums">
          {formatArr(report.recoverable_arr)}
        </h2>
        <p className="mt-2 text-body text-gray-600">Estimated Recoverable ARR</p>
        <div className="mt-8 flex flex-wrap justify-center gap-8 text-body text-gray-600">
          <div>
            <span className="font-medium text-gray-900 tabular-nums">{report.finding_count}</span>{" "}
            findings
          </div>
          <div>
            <span className="font-medium text-gray-900 tabular-nums">{report.rules_completed}</span>{" "}
            rules executed
          </div>
          {report.overall_confidence && (
            <div>
              <span className="font-medium text-gray-900 tabular-nums">
                {report.overall_confidence}%
              </span>{" "}
              confidence
            </div>
          )}
        </div>
      </section>

      <ScanPipeline
        status={report.status}
        rulesCompleted={report.rules_completed}
        rulesTotal={report.rules_total}
      />

      <div className="flex flex-wrap items-center gap-4">
        <Button disabled>View Full Summary</Button>
        <Link
          href="/validation"
          className="inline-flex h-12 items-center justify-center rounded-button border border-gray-200 bg-white px-6 text-body font-medium text-primary hover:border-gray-300"
        >
          Back to Validation
        </Link>
      </div>
      <p className="text-small text-gray-500">
        Detailed revenue summary and findings report will be available in Sprint 4.
      </p>
    </div>
  );
}
