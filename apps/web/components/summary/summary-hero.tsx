import { formatCurrency, type FreeSummaryResponse } from "@rlr/shared";

import { GlassCard } from "@/components/ui/glass-card";

interface SummaryHeroProps {
  summary: FreeSummaryResponse;
}

export function SummaryHero({ summary }: SummaryHeroProps) {
  return (
    <GlassCard padding="lg" elevated>
      <p className="text-overline uppercase text-gray-500">Revenue Verification Summary</p>
      <h2 className="mt-4 text-metric-xl font-semibold tabular-nums text-gray-900">
        {formatCurrency(summary.recoverable_arr)}
      </h2>
      <p className="mt-2 text-body text-gray-600">Estimated Recoverable ARR</p>

      <div className="mt-10 grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
        <Metric label="Confidence" value={summary.confidence ? `${summary.confidence}%` : "—"} />
        <Metric label="Verification Checks" value={`${summary.rules_completed}/${summary.rules_total}`} />
        <Metric label="Potential Findings" value={String(summary.finding_count)} />
        <Metric label="Accounts Reviewed" value={String(summary.accounts_reviewed)} />
        <Metric label="Invoices Reviewed" value={String(summary.invoices_reviewed)} />
      </div>
    </GlassCard>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="glass-subtle rounded-card p-5">
      <p className="text-caption text-gray-500">{label}</p>
      <p className="mt-2 text-h4 font-semibold tabular-nums text-gray-900">{value}</p>
    </div>
  );
}
