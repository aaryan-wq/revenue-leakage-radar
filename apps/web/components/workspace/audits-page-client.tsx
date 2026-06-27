"use client";

import Link from "next/link";
import { useState } from "react";

import { Reveal } from "@/components/motion";
import { AuditsTable } from "@/components/workspace/audits-table";
import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getStoredAuditSession } from "@/lib/audit-session";
import { sortAuditsByValue, useWorkspaceDashboard } from "@/lib/hooks/use-workspace-dashboard";
import { useAppAuth } from "@/lib/app-auth";
import {
  deleteAudit,
  downloadReportCsv,
  downloadReportPdf,
} from "@/lib/report-api";
import { ApiError } from "@/lib/api";
import { toast } from "@/lib/toast";

export function AuditsPageClient() {
  const { getToken } = useAppAuth();
  const { dashboard, isLoading, error, reload } = useWorkspaceDashboard();
  const [downloadingId, setDownloadingId] = useState<string | null>(null);
  const [downloadingCsvId, setDownloadingCsvId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  const handleDownload = async (reportId: string) => {
    setDownloadingId(reportId);
    try {
      const session = getStoredAuditSession();
      const authToken = await getToken();
      await downloadReportPdf(reportId, session, authToken);
      toast.success("PDF downloaded.");
    } catch {
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
      await reload();
    } catch (err) {
      const message = err instanceof ApiError ? err.message : "Unable to delete audit.";
      toast.error(message);
    } finally {
      setDeletingId(null);
    }
  };

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading audits…" />;
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

  const audits = dashboard ? sortAuditsByValue(dashboard.audits) : [];

  return (
    <div className="mx-auto max-w-marketing px-6 py-12 md:px-10">
      <Reveal>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">Audits</p>
            <h1 className="mt-2 font-heading text-3xl tracking-tight">Audit history</h1>
            <p className="mt-2 text-muted-foreground">
              Every verification run with status, coverage, and estimated recoverable ARR.
            </p>
          </div>
          <Link href="/upload">
            <Button>Start New Audit</Button>
          </Link>
        </div>
      </Reveal>

      {audits.length === 0 ? (
        <div className="mt-16 text-center">
          <p className="text-muted-foreground">No audits yet.</p>
          <Link href="/upload" className="mt-6 inline-block">
            <Button>Start New Audit</Button>
          </Link>
        </div>
      ) : (
        <div className="mt-10">
          <AuditsTable
            audits={audits}
            showPlatform
            onDownloadPdf={(id) => void handleDownload(id)}
            onDownloadCsv={(id) => void handleDownloadCsv(id)}
            onDelete={(id) => void handleDelete(id)}
            downloadingId={downloadingId}
            downloadingCsvId={downloadingCsvId}
            deletingId={deletingId}
          />
        </div>
      )}
    </div>
  );
}
