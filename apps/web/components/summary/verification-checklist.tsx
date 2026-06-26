import { AlertTriangle, CheckCircle2, CircleDashed, Info, XCircle } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { formatCurrency, type VerificationCheckItem } from "@rlr/shared";

interface VerificationChecklistProps {
  checks: VerificationCheckItem[];
}

const STATUS_CONFIG = {
  passed: {
    label: "Passed",
    icon: CheckCircle2,
    className: "text-success",
  },
  issues_found: {
    label: "Issues Found",
    icon: AlertTriangle,
    className: "text-warning",
  },
  partial: {
    label: "Partial Coverage",
    icon: Info,
    className: "text-warning",
  },
  not_run: {
    label: "Not Run",
    icon: CircleDashed,
    className: "text-gray-400",
  },
  error: {
    label: "Error",
    icon: XCircle,
    className: "text-error",
  },
} as const;

export function VerificationChecklist({ checks }: VerificationChecklistProps) {
  return (
    <GlassCard padding="none" className="overflow-hidden">
      <div className="p-8 pb-0">
        <h3 className="text-h3 font-semibold text-gray-900">Verification Checks</h3>
        <p className="mt-2 text-body text-gray-500">
          Deterministic rules executed against your billing data. Partial checks ran with reduced dataset coverage.
        </p>
      </div>
      <div className="mt-8 overflow-x-auto px-2 pb-2">
        <table className="w-full min-w-[640px] text-left text-body">
          <thead className="sticky top-0 bg-surface-glass-elevated backdrop-blur-lg">
            <tr className="border-b border-border text-caption text-gray-500">
              <th className="px-6 py-4 font-medium">Check</th>
              <th className="px-6 py-4 font-medium">Status</th>
              <th className="px-6 py-4 text-right font-medium">Findings</th>
              <th className="px-6 py-4 text-right font-medium">Est. ARR</th>
            </tr>
          </thead>
          <tbody>
            {checks.map((check) => {
              const config = STATUS_CONFIG[check.status] ?? STATUS_CONFIG.not_run;
              const Icon = config.icon;
              const note = check.coverage_note ?? check.skip_reason;
              return (
                <tr key={check.rule_id} className="border-b border-border transition-colors hover:bg-surface-glass-subtle">
                  <td className="px-6 py-4">
                    <p className="text-gray-900">{check.name}</p>
                    {note && <p className="mt-1 text-caption text-gray-500">{note}</p>}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center gap-2 ${config.className}`}>
                      <Icon className="h-4 w-4" strokeWidth={1.75} />
                      {config.label}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-right tabular-nums text-gray-700">
                    {check.finding_count}
                  </td>
                  <td className="px-6 py-4 text-right tabular-nums text-gray-900">
                    {formatCurrency(check.arr)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </GlassCard>
  );
}
