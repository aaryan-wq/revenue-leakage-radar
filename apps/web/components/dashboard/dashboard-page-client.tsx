"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { Logo } from "@/components/brand/logo";
import { ArrowRight, Download, Trash2 } from "lucide-react";

import { CountUp } from "@/components/count-up";
import { Reveal } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { WorkspaceView } from "@/components/workspace/workspace-view";
import { ApiError } from "@/lib/api";
import { WORKSPACE_UPLOAD_HREF, getStoredAuditSession } from "@/lib/audit-session";
import {
  deleteAudit,
  downloadReportCsv,
  downloadReportPdf,
  getDashboard,
  getReport,
} from "@/lib/report-api";
import {
  formatCurrency,
  type DashboardResponse,
  type FindingResponse,
} from "@rlr/shared";
import { toast } from "@/lib/toast";
import { PRODUCT_NAMES } from "@/lib/pricing-content";

export function DashboardPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [findings, setFindings] = useState<FindingResponse[]>([]);
  const [activeReportId, setActiveReportId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [downloadingCsvId, setDownloadingCsvId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadFindingsForAudit = useCallback(
    async (reportId: string, authToken: string) => {
      const session = getStoredAuditSession();
      try {
        const report = await getReport(reportId, {
          auditSession: session?.sessionToken,
          authToken,
        });
        setFindings(report.findings);
        setActiveReportId(reportId);
      } catch {
        setFindings([]);
        setActiveReportId(reportId);
      }
    },
    [],
  );

  const loadDashboard = useCallback(async () => {
    if (!isSignedIn) return;
    try {
      const token = await getToken();
      if (!token) {
        setError("Unable to load your session token. Sign out and sign in again.");
        return;
      }
      const data = await getDashboard(token);
      setDashboard(data);

      if (data.audits.length > 0) {
        const topAudit =
          [...data.audits].sort((a, b) => {
            if (a.purchased !== b.purchased) return a.purchased ? -1 : 1;
            return (
              parseFloat(b.recoverable_arr || "0") - parseFloat(a.recoverable_arr || "0")
            );
          })[0] ?? null;

        if (topAudit) {
          await loadFindingsForAudit(topAudit.report_id, token);
        }
      }

      setError(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to load dashboard. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn, loadFindingsForAudit]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/dashboard");
      return;
    }
    void loadDashboard();
  }, [isLoaded, isSignedIn, loadDashboard, router]);

  useEffect(() => {
    if (!isLoaded || !isSignedIn) return;
    if (searchParams.get("checkout") !== "success") return;

    toast.success("Your purchase is active. Review your updated account on the dashboard.");
    void loadDashboard();
    router.replace("/dashboard");
  }, [isLoaded, isSignedIn, loadDashboard, router, searchParams]);

  const handleDownload = async (reportId: string) => {
    setDownloadingId(reportId);
    try {
      const session = getStoredAuditSession();
      const authToken = await getToken();
      await downloadReportPdf(reportId, session, authToken);
      toast.success("PDF downloaded.");
    } catch {
      setError("PDF download failed.");
      toast.error("PDF download failed.");
    } finally {
      setDownloadingId(null);
    }
  };

  const handleDownloadCsv = async (reportId: string) => {
    setDownloadingCsvId(reportId);
    try {
      const session = getStoredAuditSession();
      const authToken = await getToken();
      await downloadReportCsv(reportId, session, authToken);
      toast.success("CSV downloaded.");
    } catch {
      setError("CSV download failed.");
      toast.error("CSV download failed.");
    } finally {
      setDownloadingCsvId(null);
    }
  };

  const handleDelete = async (auditId: string) => {
    if (!window.confirm("Delete this audit and all associated findings? This cannot be undone.")) {
      return;
    }
    setDeletingId(auditId);
    try {
      const authToken = await getToken();
      if (!authToken) return;
      await deleteAudit(auditId, authToken);
      toast.success("Audit deleted.");
      await loadDashboard();
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to delete audit.";
      setError(message);
    } finally {
      setDeletingId(null);
    }
  };

  const handleSelectAudit = async (reportId: string) => {
    const authToken = await getToken();
    if (!authToken) return;
    await loadFindingsForAudit(reportId, authToken);
  };

  if (!isLoaded || isLoading) {
    return <PageLoadingSkeleton message="Loading executive workspace…" variant="dashboard" />;
  }

  if (error && !dashboard) {
    return (
      <div className="px-6 py-20 text-center">
        <p className="text-lg text-muted-foreground">{error}</p>
        <Button className="mt-6" onClick={() => void loadDashboard()}>
          Retry
        </Button>
      </div>
    );
  }

  if (!dashboard || dashboard.audits.length === 0) {
    return (
      <div className="mx-auto max-w-report px-6 py-24 text-center md:px-10">
        <Logo variant="short" href={null} className="mx-auto h-16 w-16 opacity-40" />
        <h2 className="mt-6 font-heading text-2xl tracking-tight">No audits yet</h2>
        <p className="mt-3 text-muted-foreground">
          Run your first revenue verification scan to see results here.
        </p>
        <Link href={WORKSPACE_UPLOAD_HREF} className="mt-8 inline-block">
          <Button>Run Free Scan</Button>
        </Link>
      </div>
    );
  }

  const totalRecoverable = dashboard.audits.reduce(
    (sum, audit) => sum + Number.parseFloat(audit.recoverable_arr || "0"),
    0,
  );
  const totalFindings = dashboard.audits.reduce((sum, audit) => sum + audit.finding_count, 0);
  const purchasedCount = dashboard.audits.filter((audit) => audit.purchased).length;
  const nextUnpurchased = dashboard.audits.find((audit) => !audit.purchased);

  return (
    <div>
      <section className="border-b border-line">
        <div className="mx-auto max-w-marketing px-6 py-12 md:px-10">
          <Reveal>
            <div className="flex flex-wrap items-end justify-between gap-6">
              <div>
                <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
                  Revenue recovered
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
                  {totalFindings} findings across {dashboard.audits.length} audit
                  {dashboard.audits.length === 1 ? "" : "s"} · {purchasedCount} unlocked
                </p>
              </div>
              <div className="flex flex-col items-end gap-4">
                <div className="text-right">
                  <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Report credits
                  </p>
                  <p className="mt-2 font-heading text-3xl tracking-tight tnum">
                    {dashboard.reports_remaining}
                  </p>
                </div>
                {nextUnpurchased ? (
                  <Link
                    href={`/report/${nextUnpurchased.report_id}`}
                    className="inline-flex items-center gap-2 text-sm font-medium text-primary underline-offset-4 hover:underline"
                  >
                    Unlock {PRODUCT_NAMES.verificationReport}
                    <ArrowRight className="h-4 w-4" strokeWidth={1.75} />
                  </Link>
                ) : (
                  <Link href={WORKSPACE_UPLOAD_HREF}>
                    <Button size="sm">New audit</Button>
                  </Link>
                )}
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      <div className="mx-auto max-w-marketing border-b border-line">
        <WorkspaceView findings={findings} reportId={activeReportId} />
      </div>

      {findings.length === 0 && activeReportId && (
        <div className="mx-auto max-w-report border-b border-line px-6 py-10 text-center md:px-10">
          <p className="text-muted-foreground">
            Detailed findings require a purchased report.
          </p>
          <Link href={`/report/${activeReportId}`} className="mt-4 inline-block">
            <Button variant="secondary">View report</Button>
          </Link>
        </div>
      )}

      <section className="mx-auto max-w-marketing px-6 py-16 md:px-10">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
              Audit history
            </p>
            <h2 className="mt-2 font-heading text-2xl tracking-tight">All completed audits</h2>
          </div>
          <div className="flex gap-3">
            <Link href={WORKSPACE_UPLOAD_HREF}>
              <Button size="sm">New Audit</Button>
            </Link>
            <Link href="/billing">
              <Button variant="secondary" size="sm">
                Billing
              </Button>
            </Link>
          </div>
        </div>

        <div className="overflow-x-auto rounded-xl border border-line">
          <table className="w-full min-w-[720px] text-left text-sm">
            <thead>
              <tr className="border-b border-line text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 text-right font-medium">ARR Found</th>
                <th className="px-6 py-4 font-medium">Status</th>
                <th className="px-6 py-4 font-medium">Access</th>
                <th className="px-6 py-4 text-right font-medium">Findings</th>
                <th className="px-6 py-4 text-right font-medium">Actions</th>
              </tr>
            </thead>
            <tbody>
              {dashboard.audits.map((audit) => (
                <tr
                  key={audit.audit_id}
                  className={`border-b border-line transition-colors last:border-b-0 hover:bg-secondary/30 ${
                    audit.report_id === activeReportId ? "bg-secondary/20" : ""
                  }`}
                >
                  <td className="px-6 py-4 text-foreground">
                    {audit.date
                      ? new Date(audit.date).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "-"}
                  </td>
                  <td className="px-6 py-4 text-right tnum text-foreground">
                    {formatCurrency(audit.recoverable_arr)}
                  </td>
                  <td className="px-6 py-4 capitalize text-muted-foreground">
                    {audit.status.replace(/_/g, " ")}
                  </td>
                  <td className="px-6 py-4">
                    {audit.purchased ? (
                      <Badge variant="success">Purchased</Badge>
                    ) : (
                      <Badge variant="gray">Free summary</Badge>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right tnum text-muted-foreground">
                    {audit.finding_count}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex justify-end gap-2">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => void handleSelectAudit(audit.report_id)}
                      >
                        Explore
                      </Button>
                      <Link href={`/report/${audit.report_id}`}>
                        <Button variant="ghost" size="sm">
                          Open
                        </Button>
                      </Link>
                      {audit.purchased && (
                        <>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={downloadingId === audit.report_id}
                            onClick={() => void handleDownload(audit.report_id)}
                          >
                            <Download className="mr-1 h-4 w-4" strokeWidth={1.75} />
                            {downloadingId === audit.report_id ? "…" : "PDF"}
                          </Button>
                          <Button
                            variant="ghost"
                            size="sm"
                            disabled={downloadingCsvId === audit.report_id}
                            onClick={() => void handleDownloadCsv(audit.report_id)}
                          >
                            <Download className="mr-1 h-4 w-4" strokeWidth={1.75} />
                            {downloadingCsvId === audit.report_id ? "…" : "CSV"}
                          </Button>
                        </>
                      )}
                      <Button
                        variant="ghost"
                        size="sm"
                        disabled={deletingId === audit.audit_id}
                        onClick={() => void handleDelete(audit.audit_id)}
                        className="text-destructive hover:text-destructive"
                      >
                        <Trash2 className="mr-1 h-4 w-4" strokeWidth={1.75} />
                        {deletingId === audit.audit_id ? "…" : "Delete"}
                      </Button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
