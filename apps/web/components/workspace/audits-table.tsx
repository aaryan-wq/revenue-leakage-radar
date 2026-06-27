"use client";

import Link from "next/link";
import { Download, Trash2 } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { formatCurrency, type ReportListItem } from "@rlr/shared";

interface AuditsTableProps {
  audits: ReportListItem[];
  activeReportId?: string | null;
  onSelectAudit?: (reportId: string) => void;
  onDownloadPdf?: (reportId: string) => void;
  onDownloadCsv?: (reportId: string) => void;
  onDelete?: (auditId: string) => void;
  downloadingId?: string | null;
  downloadingCsvId?: string | null;
  deletingId?: string | null;
  showPlatform?: boolean;
}

export function AuditsTable({
  audits,
  activeReportId,
  onSelectAudit,
  onDownloadPdf,
  onDownloadCsv,
  onDelete,
  downloadingId,
  downloadingCsvId,
  deletingId,
  showPlatform = false,
}: AuditsTableProps) {
  return (
    <div className="overflow-x-auto rounded-xl border border-line">
      <table className="w-full min-w-[760px] text-left text-sm">
        <thead>
          <tr className="border-b border-line text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
            <th className="px-6 py-4 font-medium">Date</th>
            <th className="px-6 py-4 font-medium">Status</th>
            {showPlatform && <th className="px-6 py-4 font-medium">Platform</th>}
            <th className="px-6 py-4 text-right font-medium">Est. ARR</th>
            <th className="px-6 py-4 font-medium">Access</th>
            <th className="px-6 py-4 text-right font-medium">Findings</th>
            <th className="px-6 py-4 text-right font-medium">Actions</th>
          </tr>
        </thead>
        <tbody>
          {audits.map((audit) => (
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
                  : "—"}
              </td>
              <td className="px-6 py-4 capitalize text-muted-foreground">
                {audit.status.replace(/_/g, " ")}
              </td>
              {showPlatform && (
                <td className="px-6 py-4 text-muted-foreground">CSV export</td>
              )}
              <td className="px-6 py-4 text-right font-medium tnum text-foreground">
                {formatCurrency(audit.recoverable_arr)}
              </td>
              <td className="px-6 py-4">
                {audit.purchased ? (
                  <Badge variant="success">Unlocked</Badge>
                ) : (
                  <Badge variant="gray">Free summary</Badge>
                )}
              </td>
              <td className="px-6 py-4 text-right tnum text-muted-foreground">
                {audit.finding_count}
              </td>
              <td className="px-6 py-4">
                <div className="flex justify-end gap-2">
                  {onSelectAudit && (
                    <Button variant="ghost" size="sm" onClick={() => onSelectAudit(audit.report_id)}>
                      Preview
                    </Button>
                  )}
                  <Link href={`/report/${audit.report_id}`}>
                    <Button variant="ghost" size="sm">
                      Open
                    </Button>
                  </Link>
                  {audit.purchased && onDownloadPdf && (
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={downloadingId === audit.report_id}
                      onClick={() => onDownloadPdf(audit.report_id)}
                    >
                      <Download className="mr-1 h-4 w-4" strokeWidth={1.75} />
                      PDF
                    </Button>
                  )}
                  {audit.purchased && onDownloadCsv && (
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={downloadingCsvId === audit.report_id}
                      onClick={() => onDownloadCsv(audit.report_id)}
                    >
                      <Download className="mr-1 h-4 w-4" strokeWidth={1.75} />
                      CSV
                    </Button>
                  )}
                  {onDelete && (
                    <Button
                      variant="ghost"
                      size="sm"
                      disabled={deletingId === audit.audit_id}
                      onClick={() => onDelete(audit.audit_id)}
                      className="text-destructive hover:text-destructive"
                    >
                      <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                    </Button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
