"use client";

import { useCallback, useRef, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { CheckCircle2, FileUp, Loader2, Trash2 } from "lucide-react";

import { glide } from "@/components/motion";
import { formatFileSize } from "@/lib/format-file-size";
import { cn } from "@/lib/utils";

export interface UploadFileItem {
  id: string;
  file: File;
  /** Byte size from the local file or server after rehydrate. */
  fileSizeBytes: number;
  progress: number;
  status: "pending" | "uploading" | "uploaded" | "error";
  error?: string;
}

interface UploadZoneProps {
  files: UploadFileItem[];
  onFilesSelected: (files: File[]) => void;
  onRemoveFile: (id: string) => void;
  onRetryFile?: (id: string) => void;
  removingIds?: Set<string>;
  disabled?: boolean;
}

export function UploadZone({
  files,
  onFilesSelected,
  onRemoveFile,
  onRetryFile,
  removingIds,
  disabled,
}: UploadZoneProps) {
  const [hover, setHover] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFiles = useCallback(
    (selected: FileList | null) => {
      if (!selected || disabled) return;
      const csvFiles = Array.from(selected).filter((f) => f.name.toLowerCase().endsWith(".csv"));
      if (csvFiles.length > 0) {
        onFilesSelected(csvFiles);
      }
    },
    [disabled, onFilesSelected],
  );

  return (
    <div>
      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setHover(true);
        }}
        onDragLeave={() => setHover(false)}
        onDrop={(e) => {
          e.preventDefault();
          setHover(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => !disabled && inputRef.current?.click()}
        className={cn(
          "rounded-lg border bg-background transition-colors",
          hover && !disabled ? "border-foreground" : "border-line",
          disabled ? "cursor-not-allowed opacity-50" : "cursor-pointer",
        )}
      >
        <div className="flex flex-col items-center px-8 py-16 text-center">
          <FileUp className="h-6 w-6 text-foreground" strokeWidth={1.75} />
          <h3 className="text-h4 mt-4 text-foreground">Place your data here</h3>
          <p className="mt-3 max-w-sm text-pretty leading-relaxed text-muted-foreground">
            Drop billing and CRM CSV exports, or click to browse. Files upload immediately and
            coverage updates as each export is added.
          </p>

          <input
            ref={inputRef}
            type="file"
            accept=".csv"
            multiple
            className="hidden"
            disabled={disabled}
            onChange={(e) => handleFiles(e.target.files)}
          />
        </div>
      </div>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.6, ease: glide }}
            className="mt-6 overflow-hidden"
          >
            <div className="rounded-xl border border-line bg-card">
              {files.map((item, i) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, ease: glide, delay: i * 0.06 }}
                  className="flex items-center gap-4 border-b border-line px-5 py-4 last:border-0"
                >
                  <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/10 text-primary">
                    {item.status === "uploaded" ? (
                      <CheckCircle2 className="h-4 w-4" strokeWidth={1.6} />
                    ) : (
                      <FileUp className="h-4 w-4" strokeWidth={1.6} />
                    )}
                  </span>

                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-foreground">{item.file.name}</p>
                    <p className="text-xs text-muted-foreground tnum">
                      {formatFileSize(item.fileSizeBytes)}
                      {item.status === "error" && item.error && (
                        <span className="ml-2 text-destructive">: {item.error}</span>
                      )}
                    </p>
                    {(item.status === "uploading" || item.status === "pending") && (
                      <div className="mt-2 h-1 w-full overflow-hidden rounded-full bg-secondary">
                        <motion.div
                          className="h-full bg-primary"
                          initial={{ width: 0 }}
                          animate={{ width: `${item.progress}%` }}
                          transition={{ duration: 0.2, ease: "linear" }}
                        />
                      </div>
                    )}
                  </div>

                  {item.status === "uploaded" ? (
                    <span className="text-xs uppercase tracking-wider text-primary">Uploaded</span>
                  ) : item.status === "error" ? (
                    <button
                      type="button"
                      onClick={(e) => {
                        e.stopPropagation();
                        onRetryFile?.(item.id);
                      }}
                      className="text-xs uppercase tracking-wider text-destructive underline-offset-2 hover:underline"
                    >
                      Retry
                    </button>
                  ) : (
                    <span className="text-xs uppercase tracking-wider text-muted-foreground">
                      {item.status === "uploading" ? "Uploading" : "Queued"}
                    </span>
                  )}

                  <button
                    type="button"
                    onClick={(e) => {
                      e.stopPropagation();
                      onRemoveFile(item.id);
                    }}
                    disabled={item.status === "uploading" || removingIds?.has(item.id)}
                    className="focus-ring flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground disabled:opacity-50"
                    aria-label={`Remove ${item.file.name}`}
                  >
                    {removingIds?.has(item.id) ? (
                      <Loader2 className="h-4 w-4 animate-spin" strokeWidth={1.75} />
                    ) : (
                      <Trash2 className="h-4 w-4" strokeWidth={1.75} />
                    )}
                  </button>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
