"use client";

import Link from "next/link";
import { AlertCircle, Upload } from "lucide-react";
import { useCallback, useEffect, useState } from "react";

import { Reveal } from "@/components/motion";
import { DataTierFilesChecklist } from "@/components/upload/data-tier-files-checklist";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getAuditStatus, getStoredAuditSession } from "@/lib/audit-session";
import type { DataTier, FileType } from "@rlr/shared";

export function UploadsPageClient() {
  const [uploadedTypes, setUploadedTypes] = useState<FileType[]>([]);
  const [missingRecommended, setMissingRecommended] = useState<FileType[]>([]);
  const [dataTier, setDataTier] = useState<DataTier>("insufficient");
  const [auditStatus, setAuditStatus] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [hasSession, setHasSession] = useState(false);

  const loadStatus = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) {
      setHasSession(false);
      setIsLoading(false);
      return;
    }
    setHasSession(true);
    try {
      const status = await getAuditStatus(session);
      setUploadedTypes(status.uploads.map((u) => u.file_type));
      setMissingRecommended(status.missing_recommended_file_types ?? []);
      setDataTier(status.data_tier ?? "insufficient");
      setAuditStatus(status.status);
    } catch {
      setAuditStatus("unknown");
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadStatus();
  }, [loadStatus]);

  if (isLoading) {
    return <PageLoadingSkeleton message="Loading uploads…" />;
  }

  return (
    <div className="mx-auto max-w-marketing px-6 py-12 md:px-10">
      <Reveal>
        <div className="flex flex-wrap items-end justify-between gap-4">
          <div>
            <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
              Uploads
            </p>
            <h1 className="mt-2 font-heading text-3xl tracking-tight">Upload manager</h1>
            <p className="mt-2 max-w-2xl text-muted-foreground">
              Track uploaded files, validation status, and audit readiness for your current session.
            </p>
          </div>
          <Link href="/upload">
            <Button>
              <Upload className="mr-2 h-4 w-4" strokeWidth={1.75} />
              Upload Files
            </Button>
          </Link>
        </div>
      </Reveal>

      {!hasSession ? (
        <div className="mt-12 rounded-xl border border-dashed border-line p-12 text-center">
          <Upload className="mx-auto h-10 w-10 text-muted-foreground/40" strokeWidth={1.5} />
          <p className="mt-4 text-muted-foreground">No active upload session.</p>
          <div className="mt-6 flex justify-center">
            <RunFreeAuditCta size="md" />
          </div>
        </div>
      ) : (
        <div className="mt-10 grid gap-10 lg:grid-cols-[1fr_1fr]">
          <Reveal delay={0.05}>
            <div className="rounded-xl border border-line p-6">
              <h2 className="font-heading text-lg tracking-tight">Current session</h2>
              <p className="mt-2 text-sm capitalize text-muted-foreground">
                Status: {auditStatus?.replace(/_/g, " ") ?? "—"}
              </p>
              <p className="mt-4 text-sm text-muted-foreground">
                {uploadedTypes.length} file type{uploadedTypes.length === 1 ? "" : "s"} uploaded
              </p>
              {missingRecommended.length > 0 && (
                <div className="mt-4 flex items-start gap-2 rounded-lg bg-secondary/40 p-4">
                  <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                  <p className="text-sm text-muted-foreground">
                    Add recommended files to unlock more verification rules and improve coverage.
                  </p>
                </div>
              )}
              <Link href="/upload" className="mt-6 inline-block">
                <Button variant="secondary" size="sm">
                  Re-upload or add files
                </Button>
              </Link>
            </div>
          </Reveal>

          <Reveal delay={0.1}>
            <DataTierFilesChecklist
              uploadedTypes={uploadedTypes}
              dataTier={dataTier}
              missingRecommended={missingRecommended}
            />
          </Reveal>
        </div>
      )}
    </div>
  );
}
