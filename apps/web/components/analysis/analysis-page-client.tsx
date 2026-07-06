"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useQueryClient } from "@tanstack/react-query";

import { ScanPipeline } from "@/components/analysis/scan-pipeline";
import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { useAppAuth } from "@/lib/app-auth";
import {
  ensureAuditLinked,
  getScanReport,
  getStoredAuditSession,
  isScanPollInProgress,
  isScanProcessingStatus,
  pollScanUntil,
  startScan,
} from "@/lib/audit-session";
import { ApiError } from "@/lib/api";
import { queryKeys } from "@/lib/query/keys";
import { toast } from "@/lib/toast";
import { formatCurrency, type AuditStatus, type ScanReportResponse } from "@rlr/shared";

function processingStatus(report: ScanReportResponse | null): AuditStatus {
  return report?.status ?? "ready_for_scan";
}

export function AnalysisPageClient() {
  const router = useRouter();
  const queryClient = useQueryClient();
  const { getToken, isSignedIn } = useAppAuth();
  const [report, setReport] = useState<ScanReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendComplete, setBackendComplete] = useState(false);
  const [attempt, setAttempt] = useState(0);
  const scanStartRequestedRef = useRef(false);

  const retryScan = () => {
    setError(null);
    setBackendComplete(false);
    setReport(null);
    scanStartRequestedRef.current = false;
    setAttempt((count) => count + 1);
  };

  useEffect(() => {
    async function run() {
      const session = getStoredAuditSession();
      if (!session) {
        router.replace("/upload");
        return;
      }

      try {
        let initial = await getScanReport(session);
        setReport(initial);

        if (
          initial.status === "ready_for_scan" ||
          initial.status === "processing_failed"
        ) {
          if (!scanStartRequestedRef.current) {
            scanStartRequestedRef.current = true;
            try {
              await startScan(session);
              initial = await getScanReport(session);
              setReport(initial);
            } catch (startErr) {
              initial = await getScanReport(session);
              setReport(initial);
              if (
                initial.status !== "completed" &&
                !isScanPollInProgress(initial.status)
              ) {
                throw new Error("Unable to start verification scan.");
              }
            }
          }
        } else if (
          initial.status === "scanning" ||
          initial.status === "generating_report"
        ) {
          // Scan already running. Poll only; do not POST /scan again.
          setReport(initial);
        } else if (
          initial.status !== "completed" &&
          !isScanProcessingStatus(initial.status)
        ) {
          router.replace("/validation");
          return;
        }

        if (initial.status !== "completed") {
          initial = await pollScanUntil(
            session,
            (tick) => isScanPollInProgress(tick.status),
            (tick) => setReport(tick),
            { maxAttempts: 120 },
          );
        }

        setReport(initial);
        if (initial.status === "completed") {
          if (isSignedIn) {
            const token = await getToken();
            if (token) {
              await ensureAuditLinked(token);
              void queryClient.invalidateQueries({ queryKey: queryKeys.dashboard });
            }
          }
          toast.success("Analysis complete. Your revenue summary is ready.");
        } else if (initial.scan_error || initial.status === "processing_failed") {
          setError(
            initial.scan_error ??
              "Verification scan could not be completed. Please try again.",
          );
          toast.error("Verification scan failed.");
        } else {
          setError("Analysis did not complete successfully. Please try again.");
          toast.error("Verification scan failed.");
        }
        setBackendComplete(true);
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : err instanceof Error
              ? err.message
              : "Unable to complete verification scan. Please try again.";
        setError(message);
        toast.error("Verification scan failed.");
        setBackendComplete(true);
      }
    }

    void run();
  }, [getToken, isSignedIn, queryClient, router, attempt]);

  const isProcessing = !backendComplete;

  if (isProcessing && !error) {
    return (
      <section className="mx-auto flex min-h-[50vh] max-w-processing flex-col items-center justify-center px-6 py-10 md:px-10">
        <ScanPipeline
          status={processingStatus(report)}
          rulesCompleted={report?.rules_completed ?? 0}
          rulesTotal={report?.rules_total ?? 0}
        />
      </section>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-processing px-6 py-10 md:px-10">
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-body text-foreground">{error}</p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            <Button onClick={retryScan}>Retry Scan</Button>
            <Button variant="secondary" onClick={() => router.replace("/validation")}>
              Back to Validation
            </Button>
          </div>
        </GlassCard>
      </div>
    );
  }

  if (!report || report.status !== "completed") {
    return (
      <div className="mx-auto max-w-processing px-6 py-10 md:px-10">
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-body text-foreground">
            {report?.scan_error ??
              "Analysis did not complete successfully. Please return to validation and try again."}
          </p>
          <div className="mt-6 flex flex-wrap items-center justify-center gap-4">
            <Button onClick={retryScan}>Retry Scan</Button>
            <Button variant="secondary" onClick={() => router.replace("/validation")}>
              Back to Validation
            </Button>
          </div>
        </GlassCard>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-processing space-y-16 px-6 py-10 md:px-10">
      <Reveal>
        <GlassCard padding="lg" elevated className="text-center">
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Scan complete
          </p>
          <h2 className="mt-4 font-heading text-[clamp(2.5rem,7vw,4rem)] leading-none tracking-tight tnum">
            {formatCurrency(report.recoverable_arr)}
          </h2>
          <p className="mt-2 text-body text-muted-foreground">Estimated recoverable ARR</p>
          <div className="mt-8 flex flex-wrap justify-center gap-8 text-body text-muted-foreground">
            <div>
              <span className="font-heading text-foreground tnum">{report.finding_count}</span>{" "}
              findings
            </div>
            <div>
              <span className="font-heading text-foreground tnum">{report.rules_completed}</span>{" "}
              rules executed
            </div>
            {report.overall_confidence && (
              <div>
                <span className="font-heading text-foreground tnum">
                  {report.overall_confidence}%
                </span>{" "}
                confidence
              </div>
            )}
          </div>
        </GlassCard>
      </Reveal>

      <ScanPipeline
        status={report.status}
        rulesCompleted={report.rules_completed}
        rulesTotal={report.rules_total}
      />

      <div className="flex flex-wrap items-center gap-4">
        <Link href="/summary">
          <Button>View Full Summary</Button>
        </Link>
        <Link href="/validation">
          <Button variant="secondary">Back to Validation</Button>
        </Link>
      </div>
    </div>
  );
}
