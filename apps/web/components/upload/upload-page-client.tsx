"use client";

import { useCallback, useEffect, useState } from "react";
import { AlertCircle, Loader2 } from "lucide-react";

import { RequiredFilesChecklist } from "@/components/upload/required-files-checklist";
import { UploadZone, type UploadFileItem } from "@/components/upload/upload-zone";
import { Button } from "@/components/ui/button";
import {
  createAuditSession,
  getAuditStatus,
  getStoredAuditSession,
  uploadFiles,
} from "@/lib/audit-session";
import type { FileType } from "@rlr/shared";
import { REQUIRED_BILLING_FILES } from "@rlr/shared";

function generateId(): string {
  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function UploadPageClient() {
  const [files, setFiles] = useState<UploadFileItem[]>([]);
  const [uploadedTypes, setUploadedTypes] = useState<FileType[]>([]);
  const [isInitializing, setIsInitializing] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [auditReady, setAuditReady] = useState(false);

  useEffect(() => {
    async function init() {
      try {
        let session = getStoredAuditSession();
        if (!session) {
          session = await createAuditSession();
        }
        const status = await getAuditStatus(session);
        setUploadedTypes(status.uploads.map((u) => u.file_type));
        setAuditReady(true);
      } catch {
        setError("Unable to start audit session. Please refresh and try again.");
      } finally {
        setIsInitializing(false);
      }
    }
    void init();
  }, []);

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

      const status = await getAuditStatus(session);
      setUploadedTypes(status.uploads.map((u) => u.file_type));
    } catch (err) {
      const message = err instanceof Error ? err.message : "Upload failed";
      setError(message);
      setFiles((prev) =>
        prev.map((f) => ({ ...f, status: "error" as const, error: message })),
      );
    } finally {
      setIsUploading(false);
    }
  }, [files]);

  const allRequiredUploaded = REQUIRED_BILLING_FILES.every((type) =>
    uploadedTypes.includes(type),
  );

  if (isInitializing) {
    return (
      <div className="flex min-h-[400px] items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-gray-400" strokeWidth={1.75} />
      </div>
    );
  }

  return (
    <div className="grid gap-8 lg:grid-cols-3">
      <div className="lg:col-span-2">
        <UploadZone
          files={files}
          onFilesSelected={handleFilesSelected}
          onRemoveFile={handleRemoveFile}
          disabled={isUploading || !auditReady}
        />

        {error && (
          <div className="mt-6 flex items-start gap-3 rounded-card border border-error/20 bg-error-bg p-4">
            <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-error" strokeWidth={1.75} />
            <p className="text-small text-gray-700">{error}</p>
          </div>
        )}

        <div className="mt-8 flex items-center gap-4">
          <Button
            onClick={() => void handleUpload()}
            disabled={files.length === 0 || isUploading || !auditReady}
          >
            {isUploading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Uploading…
              </>
            ) : (
              "Upload Files"
            )}
          </Button>
          {allRequiredUploaded && (
            <Button variant="secondary" disabled>
              Continue to Validation
            </Button>
          )}
        </div>
        {allRequiredUploaded && (
          <p className="mt-4 text-small text-gray-500">
            All required files uploaded. Validation begins in Sprint 2.
          </p>
        )}
      </div>

      <div>
        <RequiredFilesChecklist uploadedTypes={uploadedTypes} />
      </div>
    </div>
  );
}
