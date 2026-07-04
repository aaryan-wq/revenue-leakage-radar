import type { ValidationResult } from "@rlr/shared";
import { AlertCircle, AlertTriangle, CheckCircle2 } from "lucide-react";

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
      <div
        className={cn(
          "flex items-start gap-4 rounded-xl border border-line bg-secondary/40 p-6",
        )}
      >
        <AlertCircle className="h-6 w-6 shrink-0 text-leak" strokeWidth={1.75} />
        <div>
          <h3 className="font-heading text-xl tracking-tight text-foreground">Blocking errors found</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Fix the issues below and re-upload your billing and CRM files to continue.
          </p>
        </div>
      </div>
    );
  }

  if (
    status === "processing_failed" &&
    (result === "ready" || result === "warnings")
  ) {
    return (
      <div
        className={cn(
          "flex items-start gap-4 rounded-xl border border-line bg-secondary/40 p-6",
        )}
      >
        <AlertTriangle className="h-6 w-6 shrink-0 text-leak" strokeWidth={1.75} />
        <div>
          <h3 className="font-heading text-xl tracking-tight text-foreground">
            Validation passed. Scan needs a retry
          </h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Your data validated successfully, but the verification scan did not finish. Continue to
            analysis to run it again.
          </p>
        </div>
      </div>
    );
  }

  if (status === "processing_failed" || ingestionError) {
    return (
      <div
        className={cn(
          "flex items-start gap-4 rounded-xl border border-line bg-secondary/40 p-6",
        )}
      >
        <AlertCircle className="h-6 w-6 shrink-0 text-leak" strokeWidth={1.75} />
        <div>
          <h3 className="font-heading text-xl tracking-tight text-foreground">Processing failed</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            {ingestionError ?? "Something went wrong during validation. Please try again."}
          </p>
        </div>
      </div>
    );
  }

  if (result === "warnings") {
    return (
      <div
        className={cn(
          "flex items-start gap-4 rounded-xl border border-line bg-secondary/40 p-6",
        )}
      >
        <AlertTriangle className="h-6 w-6 shrink-0 text-leak" strokeWidth={1.75} />
        <div>
          <h3 className="font-heading text-xl tracking-tight text-foreground">Ready with warnings</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Your data can be processed, but review the warnings below before scanning.
          </p>
        </div>
      </div>
    );
  }

  if (result === "ready" || status === "ready_for_scan") {
    return (
      <div
        className={cn(
          "flex items-start gap-4 rounded-xl border border-line bg-secondary/40 p-6",
        )}
      >
        <CheckCircle2 className="h-6 w-6 shrink-0 text-primary" strokeWidth={1.75} />
        <div>
          <h3 className="font-heading text-xl tracking-tight text-foreground">Validation complete</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Your billing and CRM data has been validated and normalized successfully.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div
      className={cn(
        "flex items-start gap-4 rounded-xl border border-line bg-secondary/40 p-6",
      )}
    >
      <AlertTriangle className="h-6 w-6 shrink-0 text-muted-foreground" strokeWidth={1.75} />
      <div>
        <h3 className="font-heading text-xl tracking-tight text-foreground">Validation status</h3>
        <p className="mt-2 text-sm text-muted-foreground">
          Review the checks below for details on your uploaded data.
        </p>
      </div>
    </div>
  );
}
