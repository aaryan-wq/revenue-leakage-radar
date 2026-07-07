"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { motion } from "framer-motion";
import { AlertCircle, Loader2 } from "lucide-react";

import { DataTierFilesChecklist } from "@/components/upload/data-tier-files-checklist";
import { LegalConsent } from "@/components/legal/legal-consent";
import { UploadZone, type UploadFileItem } from "@/components/upload/upload-zone";
import { glide, Magnetic } from "@/components/motion";
import { HairlineCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { ApiError } from "@/lib/api";
import { toast } from "@/lib/toast";
import { captureAuditEvent } from "@/lib/analytics/client";
import { AnalyticsEvents } from "@rlr/shared";
import {
  abandonAuditOnExit,
  captureAuditOriginFromSearch,
  clearAuditSession,
  createAuditSession,
  deleteUpload,
  getAuditStatus,
  getStoredAuditSession,
  uploadFiles,
} from "@/lib/audit-session";
import { hasBillingUpload, type CoverageAnalysis, type AuditStatusResponse, type DataTier, type FileType } from "@rlr/shared";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

function mergeFilesFromStatus(
  prev: UploadFileItem[],
  status: AuditStatusResponse,
): UploadFileItem[] {
  const inFlight = prev.filter(
    (item) =>
      item.status === "pending" ||
      item.status === "uploading" ||
      item.status === "error",
  );
  const inFlightNames = new Set(inFlight.map((item) => item.file.name));
  const fromServer = status.uploads
    .filter((upload) => !inFlightNames.has(upload.original_filename))
    .map((upload) => ({
      id: upload.id,
      file: new File([], upload.original_filename, { type: "text/csv" }),
      fileSizeBytes: upload.file_size,
      progress: 100,
      status: "uploaded" as const,
    }));
  return [...inFlight, ...fromServer];
}

export function UploadPageClient() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [files, setFiles] = useState<UploadFileItem[]>([]);
  const [uploadedTypes, setUploadedTypes] = useState<FileType[]>([]);
  const [missingRecommended, setMissingRecommended] = useState<FileType[]>([]);
  const [dataTier, setDataTier] = useState<DataTier>("insufficient");
  const [coverage, setCoverage] = useState<CoverageAnalysis | null>(null);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [isSyncingCoverage, setIsSyncingCoverage] = useState(false);
  const [removingIds, setRemovingIds] = useState<Set<string>>(() => new Set());
  const [error, setError] = useState<string | null>(null);
  const [auditReady, setAuditReady] = useState(false);
  const initStarted = useRef(false);
  const uploadChainRef = useRef<Promise<void>>(Promise.resolve());
  const filesRef = useRef<UploadFileItem[]>([]);

  useEffect(() => {
    filesRef.current = files;
  }, [files]);

  const syncAuditStatus = useCallback(async () => {
    const session = getStoredAuditSession();
    if (!session) return;
    setIsSyncingCoverage(true);
    try {
      const status = await getAuditStatus(session);
      setUploadedTypes(status.uploads.map((u) => u.file_type));
      setMissingRecommended(status.missing_recommended_file_types ?? []);
      setDataTier(status.data_tier ?? "insufficient");
      setCoverage(status.coverage_analysis ?? null);
      setFiles((prev) => mergeFilesFromStatus(prev, status));
      return status;
    } finally {
      setIsSyncingCoverage(false);
    }
  }, []);

  useEffect(() => {
    captureAuditOriginFromSearch(searchParams);
  }, [searchParams]);

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
            existing.status === "processing_failed" ||
            existing.status === "completed"
          ) {
            await abandonAuditOnExit();
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

  const scheduleUpload = useCallback(
    (items: UploadFileItem[]) => {
      if (items.length === 0 || !auditReady) return;

      uploadChainRef.current = uploadChainRef.current.then(async () => {
        const session = getStoredAuditSession();
        if (!session) return;

        const activeItems = items.filter((item) =>
          filesRef.current.some(
            (file) => file.id === item.id && (file.status === "pending" || file.status === "uploading"),
          ),
        );
        if (activeItems.length === 0) return;

        const ids = new Set(activeItems.map((item) => item.id));
        setIsUploading(true);
        setError(null);
        setFiles((prev) =>
          prev.map((f) =>
            ids.has(f.id) ? { ...f, status: "uploading" as const, progress: 0, error: undefined } : f,
          ),
        );

        try {
          const responses = await uploadFiles(
            session,
            activeItems.map((item) => item.file),
            (filename, progress) => {
              setFiles((prev) =>
                prev.map((f) => (f.file.name === filename ? { ...f, progress } : f)),
              );
            },
          );

          const responseByFilename = new Map(
            responses.map((response) => [response.original_filename, response]),
          );

          setFiles((prev) =>
            prev.map((f) => {
              if (!ids.has(f.id)) return f;
              const response = responseByFilename.get(f.file.name);
              if (!response) {
                return { ...f, status: "error" as const, error: "Upload response missing." };
              }
              return {
                ...f,
                id: response.id,
                fileSizeBytes: response.file_size,
                status: "uploaded" as const,
                progress: 100,
              };
            }),
          );
          await syncAuditStatus();
        } catch (err) {
          const message = err instanceof Error ? err.message : "Upload failed";
          setError(message);
          toast.error(message);
          const session = getStoredAuditSession();
          for (const item of activeItems) {
            captureAuditEvent(AnalyticsEvents.CSV_UPLOAD_FAILED, session?.auditId ?? "unknown", {
              original_filename: item.file.name,
              error: message,
            });
          }
          setFiles((prev) =>
            prev.map((f) =>
              ids.has(f.id) ? { ...f, status: "error" as const, error: message } : f,
            ),
          );
        } finally {
          setIsUploading(false);
        }
      });
    },
    [auditReady, syncAuditStatus],
  );

  const handleFilesSelected = useCallback(
    (newFiles: File[]) => {
      setError(null);
      const existingNames = new Set(filesRef.current.map((f) => f.file.name));
      const additions: UploadFileItem[] = [];

      for (const file of newFiles) {
        if (existingNames.has(file.name)) continue;
        additions.push({
          id: generateId(),
          file,
          fileSizeBytes: file.size,
          progress: 0,
          status: "pending",
        });
        existingNames.add(file.name);
      }

        if (additions.length === 0) return;

      for (const item of additions) {
        const session = getStoredAuditSession();
        captureAuditEvent(AnalyticsEvents.CSV_UPLOAD_STARTED, session?.auditId ?? "unknown", {
          original_filename: item.file.name,
          file_size_bytes: item.file.size,
        });
      }

      setFiles((prev) => [...prev, ...additions]);
      scheduleUpload(additions);
    },
    [scheduleUpload],
  );

  const handleRemoveFile = useCallback(
    async (id: string) => {
      const item = filesRef.current.find((file) => file.id === id);
      if (!item || item.status === "uploading") return;

      setRemovingIds((prev) => new Set(prev).add(id));
      setError(null);
      setFiles((prev) => prev.filter((file) => file.id !== id));

      if (item.status === "uploaded") {
        const session = getStoredAuditSession();
        if (!session) {
          setRemovingIds((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
          return;
        }

        try {
          await deleteUpload(session, id);
          await syncAuditStatus();
        } catch (err) {
          const message = err instanceof Error ? err.message : "Unable to remove file.";
          setError(message);
          toast.error(message);
          setFiles((prev) => [...prev, item]);
        } finally {
          setRemovingIds((prev) => {
            const next = new Set(prev);
            next.delete(id);
            return next;
          });
        }
        return;
      }

      setRemovingIds((prev) => {
        const next = new Set(prev);
        next.delete(id);
        return next;
      });
    },
    [syncAuditStatus],
  );

  const handleRetryFile = useCallback(
    (id: string) => {
      const item = filesRef.current.find((f) => f.id === id);
      if (!item || item.status !== "error") return;
      const retryItem: UploadFileItem = {
        ...item,
        status: "pending",
        progress: 0,
        error: undefined,
      };
      setFiles((prev) => prev.map((f) => (f.id === id ? retryItem : f)));
      scheduleUpload([retryItem]);
    },
    [scheduleUpload],
  );

  const handleContinueToValidation = useCallback(async () => {
    setError(null);
    await uploadChainRef.current;

    const session = getStoredAuditSession();
    if (!session) {
      toast.error("Upload session expired. Please refresh and try again.");
      return;
    }

    try {
      const status = await getAuditStatus(session);
      if (!(status.has_billing_upload ?? status.required_files_present)) {
        toast.error("Upload at least one recognized billing CSV before continuing.");
        return;
      }
    } catch {
      toast.error("Unable to verify uploads. Please try again.");
      return;
    }

    router.push("/validation");
  }, [router]);

  const billingUploadReady = hasBillingUpload(uploadedTypes);
  const uploadingCount = files.filter((f) => f.status === "uploading").length;
  const pendingCount = files.filter((f) => f.status === "pending").length;
  const uploadedCount = files.filter((f) => f.status === "uploaded").length;
  const uploadsInFlight =
    isUploading || isSyncingCoverage || uploadingCount > 0 || pendingCount > 0;
  const canContinueToValidation = billingUploadReady && !uploadsInFlight;
  const readyLabel =
    uploadingCount > 0
      ? `Uploading ${uploadingCount} file${uploadingCount > 1 ? "s" : ""}…`
      : uploadedCount > 0
        ? `${uploadedCount} file${uploadedCount > 1 ? "s" : ""} received${
            coverage ? ` · ${coverage.rules_available}/${coverage.rules_total} rules available` : ""
          }`
        : "Drop a billing CSV to begin";

  if (isInitializing) {
    return <PageLoadingSkeleton message="Preparing upload session…" variant="default" />;
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
          Upload any billing CSV export to start a free revenue verification scan. Add more files
          anytime to unlock additional checks. We run every rule your data supports.
        </p>
      </motion.div>

      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 1, ease: glide, delay: 0.15 }}
        className="mt-12 space-y-10"
      >
        <div className="w-full">
          <UploadZone
            files={files}
            onFilesSelected={handleFilesSelected}
            onRemoveFile={(id) => void handleRemoveFile(id)}
            onRetryFile={handleRetryFile}
            removingIds={removingIds}
            disabled={!auditReady}
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
          coverage={coverage}
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
          {billingUploadReady && (
            <p className="mt-2 text-sm text-muted-foreground">
              Coverage updates as you add files.
              {missingRecommended.length > 0 &&
                " Add more exports anytime to unlock additional verification rules."}
            </p>
          )}
        </div>

        <div className="flex flex-wrap items-center gap-4">
          {billingUploadReady && (
            <Magnetic strength={0.3}>
              <button
                type="button"
                onClick={() => void handleContinueToValidation()}
                disabled={!canContinueToValidation}
                className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {uploadsInFlight ? "Waiting for uploads…" : "Continue to Validation →"}
              </button>
            </Magnetic>
          )}
          {(isUploading || isSyncingCoverage) && (
            <span className="inline-flex items-center gap-2 text-sm text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              {isUploading ? "Uploading files…" : "Analyzing coverage…"}
            </span>
          )}
        </div>
      </motion.div>

      <LegalConsent action="uploading data" className="mt-6" />
    </section>
  );
}
