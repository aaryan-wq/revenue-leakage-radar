"use client";

import Link from "next/link";
import { Download, FileText } from "lucide-react";
import { useState } from "react";

import { Reveal } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getStoredAuditSession } from "@/lib/audit-session";
import {
  sortAuditsByValue,
  useWorkspaceDashboard,
} from "@/lib/hooks/use-workspace-dashboard";
import { useAppAuth } from "@/lib/app-auth";
import { downloadReportCsv, downloadReportPdf } from "@/lib/report-api";
import { formatCurrency } from "@rlr/shared";
import { toast } from "@/lib/toast";

export function ReportsPageClient() {
  const { getToken } = useAppAuth();
  const { dashboard, isLoading, error, reload } = useWorkspaceDashboard();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);

  const handleDownload = async (reportId: string, format: "pdf" | "csv") => {
    setDownloadingId(`${reportId}-${format}`);
    try {
      const session = getStoredAuditSession();
      const authToken = await getToken();
      if (format === "pdf") {
        await downloadReportPdf(reportId, session, authToken);
      } else {
        await downloadReportCsv(reportId, session, authToken);
      }
      toast.success(`${format.toUpperCase()} downloaded.`);
    } catch {
      toast.error("Download failed.");
    } finally {
      setDownloadingId(null);
    }
  };

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading reports…" />;
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

  const reports = dashboard ? sortAuditsByValue(dashboard.audits) : [];

  return (
    <div className="mx-auto max-w-marketing px-6 py-12 md:px-10">
      <Reveal>
        <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">Reports</p>
        <h1 className="mt-2 font-heading text-3xl tracking-tight">Report library</h1>
        <p className="mt-2 max-w-2xl text-muted-foreground">
          Historical reports with exports. Compare recoverable ARR over time as you run recurring
          audits.
        </p>
      </Reveal>

      {reports.length === 0 ? (
        <div className="mt-16 rounded-xl border border-dashed border-line p-12 text-center">
          <FileText className="mx-auto h-10 w-10 text-muted-foreground/40" strokeWidth={1.5} />
          <p className="mt-4 text-muted-foreground">No reports yet. Complete an audit to generate one.</p>
          <Link href="/upload" className="mt-6 inline-block">
            <Button>Start New Audit</Button>
          </Link>
        </div>
      ) : (
        <div className="mt-10 space-y-4">
          {reports.map((report) => (
            <div
              key={report.report_id}
              className="flex flex-wrap items-center justify-between gap-4 rounded-xl border border-line p-6 transition-colors hover:bg-secondary/20"
            >
              <div>
                <div className="flex items-center gap-3">
                  <p className="font-medium text-foreground">
                    {report.date
                      ? new Date(report.date).toLocaleDateString("en-US", {
                          month: "long",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "Audit report"}
                  </p>
                  {report.purchased ? (
                    <Badge variant="success">Unlocked</Badge>
                  ) : (
                    <Badge variant="gray">Summary only</Badge>
                  )}
                </div>
                <p className="mt-1 text-sm text-muted-foreground">
                  {formatCurrency(report.recoverable_arr)} recoverable · {report.finding_count}{" "}
                  findings
                </p>
              </div>
              <div className="flex flex-wrap gap-2">
                <Link href={`/report/${report.report_id}`}>
                  <Button variant="secondary" size="sm">
                    Open
                  </Button>
                </Link>
                {report.purchased && (
                  <>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={downloadingId === `${report.report_id}-pdf`}
                      onClick={() => void handleDownload(report.report_id, "pdf")}
                    >
                      <Download className="mr-1 h-4 w-4" strokeWidth={1.75} />
                      PDF
                    </Button>
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={downloadingId === `${report.report_id}-csv`}
                      onClick={() => void handleDownload(report.report_id, "csv")}
                    >
                      <Download className="mr-1 h-4 w-4" strokeWidth={1.75} />
                      CSV
                    </Button>
                  </>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      <Reveal delay={0.1} className="mt-12 rounded-xl border border-dashed border-line p-6">
        <p className="text-sm font-medium text-foreground">Compare reports over time</p>
        <p className="mt-2 text-sm text-muted-foreground">
          Trend analysis and version history are available with Annual Membership. Run multiple audits
          to track recovery progress quarter over quarter.
        </p>
      </Reveal>
    </div>
  );
}
