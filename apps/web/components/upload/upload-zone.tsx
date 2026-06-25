"use client";

import { useCallback, useRef, useState } from "react";
import { CheckCircle2, FileUp, Trash2, Upload } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export interface UploadFileItem {
  id: string;
  file: File;
  progress: number;
  status: "pending" | "uploading" | "uploaded" | "error";
  error?: string;
}

interface UploadZoneProps {
  files: UploadFileItem[];
  onFilesSelected: (files: File[]) => void;
  onRemoveFile: (id: string) => void;
  disabled?: boolean;
}

export function UploadZone({ files, onFilesSelected, onRemoveFile, disabled }: UploadZoneProps) {
  const [isDragging, setIsDragging] = useState(false);
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
    <div className="space-y-6">
      <div
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        onDragOver={(e) => {
          e.preventDefault();
          if (!disabled) setIsDragging(true);
        }}
        onDragLeave={() => setIsDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setIsDragging(false);
          handleFiles(e.dataTransfer.files);
        }}
        onClick={() => !disabled && inputRef.current?.click()}
        className={cn(
          "flex min-h-[280px] cursor-pointer flex-col items-center justify-center rounded-card border-2 border-dashed p-12 text-center transition-all duration-normal",
          isDragging
            ? "border-blue bg-blue-light"
            : "border-gray-200 bg-white hover:border-gray-300",
          disabled && "cursor-not-allowed opacity-50",
        )}
      >
        <div
          className={cn(
            "mb-6 flex h-16 w-16 items-center justify-center rounded-full",
            isDragging ? "bg-blue/10" : "bg-gray-100",
          )}
        >
          <Upload className="h-8 w-8 text-gray-500" strokeWidth={1.75} />
        </div>
        <p className="text-h4 text-gray-900">Drop your billing CSVs here</p>
        <p className="mt-2 max-w-reading text-small text-gray-500">
          Required: subscriptions, invoices, invoice line items, coupons, and price catalog.
          CRM exports are optional.
        </p>
        <Button variant="secondary" size="sm" className="mt-8" type="button" disabled={disabled}>
          Browse Files
        </Button>
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

      {files.length > 0 && (
        <ul className="space-y-3">
          {files.map((item) => (
            <li
              key={item.id}
              className="flex items-center gap-4 rounded-card border border-gray-100 bg-white p-4 shadow-card"
            >
              <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gray-50">
                {item.status === "uploaded" ? (
                  <CheckCircle2 className="h-5 w-5 text-success" strokeWidth={1.75} />
                ) : (
                  <FileUp className="h-5 w-5 text-gray-400" strokeWidth={1.75} />
                )}
              </div>

              <div className="min-w-0 flex-1">
                <p className="truncate text-body font-medium text-gray-900">{item.file.name}</p>
                <p className="text-caption text-gray-500">
                  {(item.file.size / 1024).toFixed(1)} KB
                  {item.status === "error" && item.error && (
                    <span className="ml-2 text-error">— {item.error}</span>
                  )}
                </p>
                {(item.status === "uploading" || item.status === "pending") && (
                  <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-gray-100">
                    <div
                      className="h-full bg-blue transition-all duration-normal"
                      style={{ width: `${item.progress}%` }}
                    />
                  </div>
                )}
              </div>

              <button
                type="button"
                onClick={() => onRemoveFile(item.id)}
                disabled={item.status === "uploading"}
                className="flex h-11 w-11 items-center justify-center rounded-button text-gray-400 hover:bg-gray-50 hover:text-gray-700 disabled:opacity-50"
                aria-label={`Remove ${item.file.name}`}
              >
                <Trash2 className="h-5 w-5" strokeWidth={1.75} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
