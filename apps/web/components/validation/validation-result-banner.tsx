import type { ValidationResult } from "@rlr/shared";
import { CheckCircle2, AlertCircle, AlertTriangle } from "lucide-react";

import { cn } from "@/lib/utils";

interface ValidationResultBannerProps {
  result: ValidationResult | null | undefined;
  status: string;
  ingestionError?: string | null;
}

export function ValidationResultBanner({
  result,
  status,
  ingestionError,
}: ValidationResultBannerProps) {
  if (status === "validation_failed" || result === "blocking") {
    return (
      <div className={cn("flex items-start gap-4 rounded-card border p-6", "border-error/20 bg-error-bg")}>
        <AlertCircle className="h-6 w-6 shrink-0 text-error" strokeWidth={1.75} />
        <div>
          <h3 className="text-h4 text-gray-900">Blocking errors found</h3>
          <p className="mt-2 text-small text-gray-600">
            Fix the issues below and re-upload your billing files to continue.
          </p>
        </div>
      </div>
    );
  }

  if (status === "processing_failed" || ingestionError) {
    return (
      <div className={cn("flex items-start gap-4 rounded-card border p-6", "border-error/20 bg-error-bg")}>
        <AlertCircle className="h-6 w-6 shrink-0 text-error" strokeWidth={1.75} />
        <div>
          <h3 className="text-h4 text-gray-900">Processing failed</h3>
          <p className="mt-2 text-small text-gray-600">
            {ingestionError ?? "Something went wrong during validation. Please try again."}
          </p>
        </div>
      </div>
    );
  }

  if (result === "warnings") {
    return (
      <div className={cn("flex items-start gap-4 rounded-card border p-6", "border-warning/20 bg-warning-bg")}>
        <AlertTriangle className="h-6 w-6 shrink-0 text-warning" strokeWidth={1.75} />
        <div>
          <h3 className="text-h4 text-gray-900">Ready with warnings</h3>
          <p className="mt-2 text-small text-gray-600">
            Your data can be processed, but review the warnings below before scanning.
          </p>
        </div>
      </div>
    );
  }

  if (result === "ready" || status === "ready_for_scan") {
    return (
      <div className={cn("flex items-start gap-4 rounded-card border p-6", "border-success/20 bg-success-bg")}>
        <CheckCircle2 className="h-6 w-6 shrink-0 text-success" strokeWidth={1.75} />
        <div>
          <h3 className="text-h4 text-gray-900">Validation complete</h3>
          <p className="mt-2 text-small text-gray-600">
            Your billing data has been validated and normalized successfully.
          </p>
        </div>
      </div>
    );
  }

  return null;
}
