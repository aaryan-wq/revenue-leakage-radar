"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";

import { AnimatedScanPipeline } from "@/components/analysis/animated-scan-pipeline";
import { ScanPipeline } from "@/components/analysis/scan-pipeline";
import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import {
  getScanReport,
  getStoredAuditSession,
  isScanProcessingStatus,
  pollScanUntil,
  startScan,
} from "@/lib/audit-session";
import { toast } from "@/lib/toast";
import { formatCurrency, type ScanReportResponse } from "@rlr/shared";

export function AnalysisPageClient() {
  const router = useRouter();
  const [report, setReport] = useState<ScanReportResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [backendComplete, setBackendComplete] = useState(false);
  const [animationComplete, setAnimationComplete] = useState(false);

  const handleAnimationComplete = useCallback(() => {
    setAnimationComplete(true);
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
        setReport(initial);

        if (initial.status === "ready_for_scan") {
          try {
            await startScan(session);
          } catch {
            initial = await getScanReport(session);
            setReport(initial);
            if (
              initial.status !== "completed" &&
              !isScanProcessingStatus(initial.status)
            ) {
              throw new Error("Unable to start verification scan.");
            }
          }
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
            (tick) => isScanProcessingStatus(tick.status),
            (tick) => setReport(tick),
          );
        }

        setReport(initial);
        if (initial.status === "completed") {
          toast.success("Analysis complete. Your revenue summary is ready.");
        }
        setBackendComplete(true);
      } catch {
        setError("Unable to complete verification scan. Please try again.");
        toast.error("Verification scan failed.");
        setBackendComplete(true);
        setAnimationComplete(true);
      }
    }

    void run();
  }, [router]);

  const isProcessing = !backendComplete || !animationComplete;

  if (isProcessing && !error) {
    return (
      <section className="mx-auto flex min-h-[50vh] max-w-processing flex-col items-center justify-center px-6 py-10 md:px-10">
        <AnimatedScanPipeline
          rulesCompleted={report?.rules_completed ?? 0}
          rulesTotal={report?.rules_total ?? 0}
          onCycleComplete={handleAnimationComplete}
        />
      </section>
    );
  }

  if (error) {
    return (
      <div className="mx-auto max-w-processing px-6 py-10 md:px-10">
        <GlassCard padding="md" className="border-line bg-secondary/40 text-center">
          <p className="text-body text-foreground">{error}</p>
          <Button className="mt-6" onClick={() => router.replace("/validation")}>
            Back to Validation
          </Button>
        </GlassCard>
      </div>
    );
  }

  if (!report || report.status !== "completed") return null;

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
