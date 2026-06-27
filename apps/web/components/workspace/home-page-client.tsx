"use client";

import Link from "next/link";
import { ArrowRight, Radar } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

import { CountUp } from "@/components/count-up";
import { Reveal } from "@/components/motion";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { AuditsTable } from "@/components/workspace/audits-table";
import { WorkspaceView } from "@/components/workspace/workspace-view";
import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getStoredAuditSession } from "@/lib/audit-session";
import {
  sortAuditsByValue,
  totalRecoverableArr,
  useWorkspaceDashboard,
} from "@/lib/hooks/use-workspace-dashboard";
import { getReport } from "@/lib/report-api";
import { useAppAuth } from "@/lib/app-auth";
import { formatCurrency, type FindingResponse } from "@rlr/shared";
import { toast } from "@/lib/toast";

export function HomePageClient() {
  const searchParams = useSearchParams();
  const { getToken } = useAppAuth();
  const { dashboard, isLoading, error, reload } = useWorkspaceDashboard();
  const [findings, setFindings] = useState<FindingResponse[]>([]);
  const [activeReportId, setActiveReportId] = useState<string | null>(null);

  const loadTopFindings = useCallback(async () => {
    if (!dashboard || dashboard.audits.length === 0) return;
    const topAudit = sortAuditsByValue(dashboard.audits)[0];
    if (!topAudit) return;

    setActiveReportId(topAudit.report_id);
    const token = await getToken();
    const session = getStoredAuditSession();
    try {
      const report = await getReport(topAudit.report_id, {
        auditSession: session?.sessionToken,
        authToken: token,
      });
      setFindings(report.findings.slice(0, 5));
    } catch {
      setFindings([]);
    }
  }, [dashboard, getToken]);

  useEffect(() => {
    void loadTopFindings();
  }, [loadTopFindings]);

  useEffect(() => {
    if (searchParams.get("checkout") === "success") {
      toast.success("Purchase complete. Your report credits have been updated.");
      void reload();
    }
  }, [reload, searchParams]);

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading workspace…" />;
  }

  if (error && !dashboard) {
    return (
      <div className="px-6 py-20 text-center">
        <p className="text-lg text-muted-foreground">{error}</p>
        <Button className="mt-6" onClick={() => void reload()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!dashboard || dashboard.audits.length === 0) {
    return (
      <div className="mx-auto max-w-report px-6 py-24 text-center md:px-10">
        <Radar className="mx-auto h-12 w-12 text-muted-foreground/40" strokeWidth={1.5} />
        <h2 className="mt-6 font-heading text-2xl tracking-tight">No audits yet</h2>
        <p className="mt-3 text-muted-foreground">
          Run your first free audit to see recoverable revenue here.
        </p>
        <div className="mt-8 flex justify-center">
          <RunFreeAuditCta size="md" />
        </div>
      </div>
    );
  }

  const recoverable = totalRecoverableArr(dashboard.audits);
  const recentAudits = sortAuditsByValue(dashboard.audits).slice(0, 3);
  const nextUnpurchased = dashboard.audits.find((audit) => !audit.purchased);
  const totalFindings = dashboard.audits.reduce((sum, a) => sum + a.finding_count, 0);

  return (
    <div>
      <section className="border-b border-line">
        <div className="mx-auto max-w-marketing px-6 py-12 md:px-10">
          <Reveal>
            <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
              Recoverable revenue
            </p>
            <div className="mt-4 font-heading text-[clamp(2.4rem,5vw,3.6rem)] leading-none tracking-tight tnum">
              <CountUp to={recoverable} prefix="$" duration={1.4} />
            </div>
            <p className="mt-3 text-muted-foreground">
              Across {dashboard.audits.length} audit{dashboard.audits.length === 1 ? "" : "s"} ·{" "}
              {totalFindings} findings · {dashboard.reports_remaining} report credits
            </p>
          </Reveal>
        </div>
      </section>

      <section className="border-b border-line">
        <div className="mx-auto max-w-marketing px-6 py-10 md:px-10">
          <Reveal>
            <h2 className="font-heading text-xl tracking-tight">Suggested next action</h2>
            <div className="mt-4 flex flex-wrap items-center justify-between gap-4 rounded-xl border border-line bg-secondary/20 p-6">
              {nextUnpurchased ? (
                <>
                  <div>
                    <p className="font-medium text-foreground">
                      Unlock your highest-value audit for full evidence
                    </p>
                    <p className="mt-1 text-sm text-muted-foreground">
                      Estimated {formatCurrency(nextUnpurchased.recoverable_arr)} recoverable ARR
                      waiting in your free summary.
                    </p>
                  </div>
                  <Link href={`/report/${nextUnpurchased.report_id}`}>
                    <Button>
                      Unlock Detailed Report
                      <ArrowRight className="ml-2 h-4 w-4" strokeWidth={1.75} />
                    </Button>
                  </Link>
                </>
              ) : (
                <>
                  <p className="text-muted-foreground">Run a new audit to find additional leakage.</p>
                  <Link href="/upload">
                    <Button>Start New Audit</Button>
                  </Link>
                </>
              )}
            </div>
          </Reveal>
        </div>
      </section>

      {findings.length > 0 && (
        <div className="mx-auto max-w-marketing border-b border-line">
          <div className="px-6 pt-10 md:px-10">
            <h2 className="font-heading text-xl tracking-tight">Recent findings</h2>
            <p className="mt-1 text-sm text-muted-foreground">From your latest audit</p>
          </div>
          <WorkspaceView findings={findings} reportId={activeReportId} />
        </div>
      )}

      <section className="mx-auto max-w-marketing px-6 py-12 md:px-10">
        <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="font-heading text-xl tracking-tight">Recent audits</h2>
            <p className="mt-1 text-sm text-muted-foreground">Your latest verification runs</p>
          </div>
          <Link href="/audits">
            <Button variant="secondary" size="sm">
              View all audits
            </Button>
          </Link>
        </div>
        <AuditsTable audits={recentAudits} activeReportId={activeReportId} />
      </section>
    </div>
  );
}
