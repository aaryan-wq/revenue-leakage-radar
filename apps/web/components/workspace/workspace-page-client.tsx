"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { Radar } from "lucide-react";

import { CountUp } from "@/components/count-up";
import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { WorkspaceView } from "@/components/workspace/workspace-view";
import { ApiError } from "@/lib/api";
import { getStoredAuditSession } from "@/lib/audit-session";
import { getDashboard, getReport } from "@/lib/report-api";
import { formatCurrency, type DashboardResponse, type FindingResponse } from "@rlr/shared";

export function WorkspacePageClient() {
  const router = useRouter();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [findings, setFindings] = useState<FindingResponse[]>([]);
  const [activeReportId, setActiveReportId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadWorkspace = useCallback(async () => {
    if (!isSignedIn) return;

    try {
      const token = await getToken();
      if (!token) {
        setError("Authentication required.");
        return;
      }

      const dashboardData = await getDashboard(token);
      setDashboard(dashboardData);

      if (dashboardData.audits.length === 0) {
        setFindings([]);
        setActiveReportId(null);
        setError(null);
        return;
      }

      const topAudit =
        [...dashboardData.audits].sort((a, b) => {
          if (a.purchased !== b.purchased) return a.purchased ? -1 : 1;
          return (
            parseFloat(b.recoverable_arr || "0") - parseFloat(a.recoverable_arr || "0")
          );
        })[0] ?? null;

      if (!topAudit) {
        setFindings([]);
        setActiveReportId(null);
        return;
      }

      setActiveReportId(topAudit.report_id);

      const session = getStoredAuditSession();
      try {
        const report = await getReport(topAudit.report_id, {
          auditSession: session?.sessionToken,
          authToken: token,
        });
        setFindings(report.findings);
      } catch {
        setFindings([]);
      }

      setError(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to load workspace. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/workspace");
      return;
    }
    void loadWorkspace();
  }, [isLoaded, isSignedIn, loadWorkspace, router]);

  if (!isLoaded || isLoading) {
    return <PageLoadingSkeleton message="Loading workspace…" />;
  }

  if (error && !dashboard) {
    return (
      <div className="px-6 py-20 text-center md:px-10">
        <p className="text-lg text-muted-foreground">{error}</p>
        <Button className="mt-6" onClick={() => void loadWorkspace()}>
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
          Run your first revenue verification scan to explore findings here.
        </p>
        <Link href="/upload" className="mt-8 inline-block">
          <Button>Run Free Scan</Button>
        </Link>
      </div>
    );
  }

  const totalRecoverable = dashboard.audits.reduce(
    (sum, audit) => sum + Number.parseFloat(audit.recoverable_arr || "0"),
    0,
  );

  return (
    <div>
      <section className="border-b border-line">
        <div className="mx-auto max-w-marketing px-6 py-12 md:px-10">
          <Reveal>
            <div className="flex flex-wrap items-end justify-between gap-6">
              <div>
                <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
                  Executive workspace
                </p>
                {dashboard.company_name && (
                  <p className="mt-2 font-heading text-xl tracking-tight">
                    {dashboard.company_name}
                  </p>
                )}
                <div className="mt-6 font-heading text-[clamp(2.4rem,5vw,3.6rem)] leading-none tracking-tight tnum">
                  <CountUp to={totalRecoverable} prefix="$" duration={1.4} />
                </div>
                <p className="mt-3 text-muted-foreground">
                  Total recoverable ARR across {dashboard.audits.length} audit
                  {dashboard.audits.length === 1 ? "" : "s"}
                </p>
              </div>
              <div className="text-right">
                <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  Report credits
                </p>
                <p className="mt-2 font-heading text-3xl tracking-tight tnum">
                  {dashboard.reports_remaining}
                </p>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      <div className="mx-auto max-w-marketing">
        <WorkspaceView findings={findings} reportId={activeReportId} />
      </div>

      {findings.length === 0 && activeReportId && (
        <div className="mx-auto max-w-report px-6 py-10 text-center md:px-10">
          <p className="text-muted-foreground">
            Detailed findings require a purchased report.
          </p>
          <Link href={`/report/${activeReportId}`} className="mt-4 inline-block">
            <Button variant="secondary">View report</Button>
          </Link>
        </div>
      )}

      <section className="border-t border-line">
        <div className="mx-auto max-w-marketing px-6 py-10 md:px-10">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <p className="text-sm text-muted-foreground">
              {formatCurrency(String(totalRecoverable))} recoverable ·{" "}
              {dashboard.reports_remaining} credits remaining
            </p>
            <div className="flex gap-3">
              <Link href="/dashboard">
                <Button variant="secondary" size="sm">
                  Audit history
                </Button>
              </Link>
              <Link href="/upload">
                <Button size="sm">New audit</Button>
              </Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
