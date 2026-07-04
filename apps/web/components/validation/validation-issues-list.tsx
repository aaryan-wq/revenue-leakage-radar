import type { ValidationIssue } from "@rlr/shared";
import { AlertCircle, AlertTriangle } from "lucide-react";

interface ValidationIssuesListProps {
  issues: ValidationIssue[];
}

export function ValidationIssuesList({ issues }: ValidationIssuesListProps) {
  if (issues.length === 0) {
    return <p className="text-sm text-muted-foreground">No validation issues found.</p>;
  }

  const blocking = issues.filter((issue) => issue.severity === "blocking");
  const warnings = issues.filter((issue) => issue.severity === "warning");

  return (
    <div className="space-y-8">
      {blocking.length > 0 && (
        <div>
          <h4 className="mb-4 font-heading text-lg tracking-tight text-leak">Blocking errors</h4>
          <ul className="space-y-3">
            {blocking.map((issue, idx) => (
              <li
                key={`${issue.code}-${idx}`}
                className="flex items-start gap-3 rounded-xl border border-line bg-secondary/40 p-4"
              >
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-leak" strokeWidth={1.75} />
                <p className="text-sm text-foreground">{issue.message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div>
          <h4 className="mb-4 font-heading text-lg tracking-tight text-muted-foreground">Warnings</h4>
          <ul className="space-y-3">
            {warnings.map((issue, idx) => (
              <li
                key={`${issue.code}-${idx}`}
                className="flex items-start gap-3 rounded-xl border border-line bg-card p-4"
              >
                <AlertTriangle
                  className="mt-0.5 h-5 w-5 shrink-0 text-muted-foreground"
                  strokeWidth={1.75}
                />
                <p className="text-sm text-foreground">{issue.message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
