import type { ValidationIssue } from "@rlr/shared";
import { AlertCircle, AlertTriangle } from "lucide-react";

interface ValidationIssuesListProps {
  issues: ValidationIssue[];
}

export function ValidationIssuesList({ issues }: ValidationIssuesListProps) {
  if (issues.length === 0) {
    return <p className="text-small text-gray-500">No validation issues found.</p>;
  }

  const blocking = issues.filter((i) => i.severity === "blocking");
  const warnings = issues.filter((i) => i.severity === "warning");

  return (
    <div className="space-y-6">
      {blocking.length > 0 && (
        <div>
          <h4 className="mb-3 text-h4 text-error">Blocking errors</h4>
          <ul className="space-y-3">
            {blocking.map((issue, idx) => (
              <li
                key={`${issue.code}-${idx}`}
                className="flex items-start gap-3 rounded-card border border-error/20 bg-error-bg p-4"
              >
                <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-error" strokeWidth={1.75} />
                <p className="text-small text-gray-700">{issue.message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}

      {warnings.length > 0 && (
        <div>
          <h4 className="mb-3 text-h4 text-warning">Warnings</h4>
          <ul className="space-y-3">
            {warnings.map((issue, idx) => (
              <li
                key={`${issue.code}-${idx}`}
                className="flex items-start gap-3 rounded-card border border-warning/20 bg-warning-bg p-4"
              >
                <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-warning" strokeWidth={1.75} />
                <p className="text-small text-gray-700">{issue.message}</p>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
