"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { AlertCircle, Loader2 } from "lucide-react";

import { DataTierFilesChecklist } from "@/components/upload/data-tier-files-checklist";
import { UploadZone, type UploadFileItem } from "@/components/upload/upload-zone";
import { glide, Magnetic } from "@/components/motion";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";
import { toast } from "@/lib/toast";
import {
  clearAuditSession,
  createAuditSession,
  getAuditStatus,
  getStoredAuditSession,
  uploadFiles,
} from "@/lib/audit-session";
import { isTier0Complete, type DataTier, type FileType } from "@rlr/shared";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function UploadPageClient() {
  const router = useRouter();
  const [files, setFiles] = useState<UploadFileItem[]>([]);
  const [uploadedTypes, setUploadedTypes] = useState<FileType[]>([]);
  const [missingRecommended, setMissingRecommended] = useState<FileType[]>([]);
  const [dataTier, setDataTier] = useState<DataTier>("insufficient");
  const [isInitializing, setIsInitializing] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [auditReady, setAuditReady] = useState(false);
  const initStarted = useRef(false);

  const syncAuditStatus = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) return;
    const status = await getAuditStatus(session);
    setUploadedTypes(status.uploads.map((u) => u.file_type));
    setMissingRecommended(status.missing_recommended_file_types ?? []);
    setDataTier(status.data_tier ?? "insufficient");
    return status;
  }, []);

  useEffect(() => {
    if (initStarted.current) return;
    initStarted.current = true;

    async function init() {
      try {
        let session = getStoredAuditSession();
        if (session) {
          const existing = await getAuditStatus(session);
          if (
            existing.status === "validation_failed" ||
            existing.status === "processing_failed"
          ) {
            clearAuditSession();
            session = null;
          }
        }
        if (!session) {
          session = await createAuditSession();
        }
        await syncAuditStatus();
        setAuditReady(true);
      } catch (err) {
        const message =
          err instanceof ApiError
            ? err.message
            : "Unable to start audit session. Make sure the backend API is running, then refresh.";
        setError(message);
      } finally {
        setIsInitializing(false);
      }
    }
    void init();
  }, [router, syncAuditStatus]);

  const handleFilesSelected = useCallback((newFiles: File[]) => {
    setError(null);
    setFiles((prev) => {
      const existingNames = new Set(prev.map((f) => f.file.name));
      const additions = newFiles
        .filter((f) => !existingNames.has(f.name))
        .map((file) => ({
          id: generateId(),
          file,
          progress: 0,
          status: "pending" as const,
        }));
      return [...prev, ...additions];
    });
  }, []);

  const handleRemoveFile = useCallback((id: string) => {
    setFiles((prev) => prev.filter((f) => f.id !== id));
  }, []);

  const handleUpload = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session || files.length === 0) return;

    setIsUploading(true);
    setError(null);

    setFiles((prev) =>
      prev.map((f) => ({ ...f, status: "uploading" as const, progress: 0 })),
    );

    try {
      await uploadFiles(
        session,
        files.map((f) => f.file),
        (filename, progress) => {
          setFiles((prev) =>
            prev.map((f) => (f.file.name === filename ? { ...f, progress } : f)),
          );
        },
      );

      setFiles((prev) =>
        prev.map((f) => ({ ...f, status: "uploaded" as const, progress: 100 })),
      );
      toast.success("Upload complete.");

      const status = await syncAuditStatus();

      if (status?.required_files_present) {
        router.push("/validation");
      }
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
      toast.error(message);
      setFiles((prev) =>
        prev.map((f) => ({ ...f, status: "error" as const, error: message })),
      );
    } finally {
      setIsUploading(false);
    }
  }, [files, router, syncAuditStatus]);

  const tier0Complete = isTier0Complete(uploadedTypes);
  const pendingCount = files.filter((f) => f.status === "pending" || f.status === "error").length;
  const readyLabel =
    files.length > 0
      ? `${files.length} file${files.length > 1 ? "s" : ""} selected${
          files.some((f) => f.status === "uploaded") ? " · some validated" : ""
        }`
      : "Awaiting your first file";

  if (isInitializing) {
    return <PageLoadingSkeleton message="Preparing upload session…" />;
  }

  return (
    <section className="mx-auto max-w-upload px-6 pt-16 pb-28 md:px-10 md:pt-24">
      <motion.div
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.9, ease: glide }}
      >
        <p className="mb-4 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Step one · Provide your data
        </p>
        <h1 className="max-w-2xl font-heading text-[clamp(2.1rem,5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
          Hand us the records. We&apos;ll find what&apos;s missing.
        </h1>
        <p className="mt-6 max-w-lg text-pretty leading-relaxed text-muted-foreground">
          Upload your billing CSV exports to begin a free revenue verification scan. The more
          systems you reconcile, the more precisely we can isolate leakage.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: glide, delay: 0.15 }}
        className="mt-12 grid gap-10 lg:grid-cols-[1.4fr_1fr]"
      >
        <div>
          <UploadZone
            files={files}
            onFilesSelected={handleFilesSelected}
            onRemoveFile={handleRemoveFile}
            disabled={isUploading || !auditReady}
          />

          {error && (
            <HairlineCard padding="sm" className="mt-6 border-destructive/30 bg-destructive/5">
              <div className="flex items-start gap-3">
                <AlertCircle
                  className="mt-0.5 h-5 w-5 shrink-0 text-destructive"
                  strokeWidth={1.75}
                />
                <p className="text-sm text-foreground">{error}</p>
              </div>
            </HairlineCard>
          )}
        </div>

        <DataTierFilesChecklist
          uploadedTypes={uploadedTypes}
          dataTier={dataTier}
          missingRecommended={missingRecommended}
        />
      </motion.div>

      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 1, delay: 0.3 }}
        className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-8"
      >
        <div>
          <p className="text-sm text-muted-foreground tnum">{readyLabel}</p>
          {tier0Complete && (
            <p className="mt-2 text-sm text-muted-foreground">
              Tier 0 files uploaded. Validation will begin automatically.
              {missingRecommended.length > 0 &&
                " Add recommended files anytime to unlock more verification rules."}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-4">
          {tier0Complete && (
            <button
              type="button"
              onClick={() => router.push("/validation")}
              className="inline-flex items-center gap-2 rounded-full border border-foreground/15 px-6 py-3.5 text-[0.92rem] transition-colors hover:bg-foreground hover:text-background"
            >
              Continue to Validation
            </button>
          )}
          <Magnetic strength={0.3}>
            <button
              type="button"
              onClick={() => void handleUpload()}
              disabled={pendingCount === 0 || isUploading || !auditReady}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50 disabled:cursor-not-allowed disabled:opacity-50"
            >
              {isUploading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin" />
                  Uploading…
                </>
              ) : (
                <>Upload Files →</>
              )}
            </button>
          </Magnetic>
        </div>
      </motion.div>
    </section>
  );
}
