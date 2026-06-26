"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams, useRouter, useSearchParams } from "next/navigation";
import { useAppAuth } from "@/lib/app-auth";
import { ArrowRight, Download, Radar, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";
import { deleteAudit, downloadReportCsv, downloadReportPdf, getDashboard } from "@/lib/report-api";
import { getStoredAuditSession } from "@/lib/audit-session";
import { formatCurrency, type DashboardResponse } from "@rlr/shared";
import { toast } from "@/lib/toast";

export function DashboardPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [downloadingCsvId, setDownloadingCsvId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const loadDashboard = useCallback(async () => {
    if (!isSignedIn) return;
    try {
      const token = await getToken();
      if (!token) {
        setError("Authentication required.");
        return;
      }
      const data = await getDashboard(token);
      setDashboard(data);
      setError(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to load dashboard. Please try again.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn]);

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

  if (!isLoaded || isLoading) {
    return <PageLoadingSkeleton message="Loading executive workspace…" />;
  }

  if (error && !dashboard) {
    return (
      <GlassCard padding="md" className="border-error/20 bg-error-bg text-center">
        <p className="text-body text-gray-700">{error}</p>
        <Button className="mt-6" onClick={() => void loadDashboard()}>
          Retry
        </Button>
      </GlassCard>
    );
  }

  if (!dashboard || dashboard.audits.length === 0) {
    return (
      <GlassCard padding="lg" elevated className="text-center">
        <Radar className="mx-auto h-12 w-12 text-gray-300" strokeWidth={1.5} />
        <h2 className="mt-6 text-h3 font-semibold text-gray-900">No audits yet</h2>
        <p className="mt-3 text-body text-gray-500">
          Run your first revenue verification scan to see results here.
        </p>
        <Link href="/upload" className="mt-8 inline-block">
          <Button>Run Free Scan</Button>
        </Link>
      </GlassCard>
    );
  }

  const totalRecoverable = dashboard.audits.reduce(
    (sum, audit) => sum + Number.parseFloat(audit.recoverable_arr || "0"),
    0,
  );
  const totalFindings = dashboard.audits.reduce((sum, audit) => sum + audit.finding_count, 0);
  const purchasedCount = dashboard.audits.filter((a) => a.purchased).length;
  const topAudits = [...dashboard.audits]
    .sort((a, b) => Number.parseFloat(b.recoverable_arr) - Number.parseFloat(a.recoverable_arr))
    .slice(0, 3);
  const nextUnpurchased = dashboard.audits.find((a) => !a.purchased);

  return (
    <div className="space-y-16">
      {(dashboard.company_name || dashboard.reports_remaining > 0) && (
        <div className="flex flex-wrap items-end justify-between gap-4 border-b border-border pb-8">
          <div>
            {dashboard.company_name && (
              <p className="text-h3 font-semibold text-gray-900">{dashboard.company_name}</p>
            )}
            <p className="mt-1 text-body text-gray-500">Revenue verification workspace</p>
          </div>
          <div className="text-right">
            <p className="text-caption text-gray-500">Reports Remaining</p>
            <p className="text-h3 font-semibold tabular-nums text-gray-900">
              {dashboard.reports_remaining}
            </p>
          </div>
        </div>
      )}

      <section>
        <p className="text-overline uppercase text-gray-500">Revenue Recovered</p>
        <p className="mt-4 text-metric-xl font-semibold tabular-nums text-gray-900">
          {formatCurrency(String(totalRecoverable))}
        </p>
        <p className="mt-2 text-body text-gray-500">
          Total estimated recoverable ARR across {dashboard.audits.length} audit
          {dashboard.audits.length === 1 ? "" : "s"}
        </p>
      </section>

      <section className="grid gap-8 md:grid-cols-3">
        <GlassCard padding="md">
          <p className="text-overline uppercase text-gray-500">High-Impact Audits</p>
          <ul className="mt-4 space-y-4">
            {topAudits.map((audit) => (
              <li key={audit.audit_id} className="flex items-center justify-between gap-4">
                <div className="min-w-0">
                  <p className="truncate text-body font-medium text-gray-900">
                    {audit.date
                      ? new Date(audit.date).toLocaleDateString("en-US", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "Recent audit"}
                  </p>
                  <p className="text-caption text-gray-500">{audit.finding_count} findings</p>
                </div>
                <p className="shrink-0 text-h4 font-semibold tabular-nums text-gray-900">
                  {formatCurrency(audit.recoverable_arr)}
                </p>
              </li>
            ))}
          </ul>
        </GlassCard>

        <GlassCard padding="md">
          <p className="text-overline uppercase text-gray-500">Audit Coverage</p>
          <p className="mt-4 text-h2 font-semibold tabular-nums text-gray-900">
            {dashboard.audits.length}
          </p>
          <p className="mt-2 text-body text-gray-500">Total audits completed</p>
          <div className="mt-6 space-y-2 text-small text-gray-600">
            <p>{purchasedCount} detailed reports unlocked</p>
            <p>{totalFindings} total findings identified</p>
            <p>{dashboard.reports_remaining} report credits remaining</p>
          </div>
        </GlassCard>

        <GlassCard padding="md" elevated>
          <p className="text-overline uppercase text-gray-500">Next Action</p>
          {nextUnpurchased ? (
            <>
              <p className="mt-4 text-body text-gray-700">
                Unlock your highest-value unpurchased report for full evidence.
              </p>
              <Link href={`/report/${nextUnpurchased.report_id}`} className="mt-6 inline-flex items-center gap-2 text-body font-medium text-primary underline-offset-4 hover:underline">
                Review report
                <ArrowRight className="h-4 w-4" strokeWidth={1.75} />
              </Link>
            </>
          ) : (
            <>
              <p className="mt-4 text-body text-gray-700">Run a new audit to discover additional recoverable revenue.</p>
              <Link href="/upload" className="mt-6 inline-block">
                <Button>New Audit</Button>
              </Link>
            </>
          )}
        </GlassCard>
      </section>

      <section>
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <h2 className="text-h3 font-semibold text-gray-900">Audit History</h2>
          <div className="flex gap-3">
            <Link href="/upload">
              <Button size="sm">New Audit</Button>
            </Link>
            <Link href="/billing">
              <Button variant="secondary" size="sm">
                Billing
              </Button>
            </Link>
          </div>
        </div>

        <GlassCard padding="none" className="overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full min-w-[720px] text-left text-body">
              <thead className="bg-surface-glass-subtle">
                <tr className="border-b border-border text-caption text-gray-500">
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
                    className="border-b border-border transition-colors hover:bg-surface-glass-subtle"
                  >
                    <td className="px-6 py-4 text-gray-900">
                      {audit.date
                        ? new Date(audit.date).toLocaleDateString("en-US", {
                            month: "short",
                            day: "numeric",
                            year: "numeric",
                          })
                        : "—"}
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums text-gray-900">
                      {formatCurrency(audit.recoverable_arr)}
                    </td>
                    <td className="px-6 py-4 capitalize text-gray-600">
                      {audit.status.replace(/_/g, " ")}
                    </td>
                    <td className="px-6 py-4">
                      {audit.purchased ? (
                        <Badge variant="success">Purchased</Badge>
                      ) : (
                        <Badge variant="gray">Free summary</Badge>
                      )}
                    </td>
                    <td className="px-6 py-4 text-right tabular-nums text-gray-700">
                      {audit.finding_count}
                    </td>
                    <td className="px-6 py-4">
                      <div className="flex justify-end gap-2">
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
                          className="text-error hover:text-error"
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
        </GlassCard>
      </section>
    </div>
  );
}
