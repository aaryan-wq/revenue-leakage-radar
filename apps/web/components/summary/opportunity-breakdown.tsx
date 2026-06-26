import { formatCurrency, type OpportunityBreakdownItem } from "@rlr/shared";

import { GlassCard } from "@/components/ui/glass-card";

interface OpportunityBreakdownProps {
  items: OpportunityBreakdownItem[];
}

export function OpportunityBreakdown({ items }: OpportunityBreakdownProps) {
  if (items.length === 0) {
    return (
      <GlassCard padding="md">
        <h3 className="text-h3 font-semibold text-gray-900">Opportunity Breakdown</h3>
        <p className="mt-4 text-body text-gray-500">No recoverable opportunities identified.</p>
      </GlassCard>
    );
  }

  return (
    <GlassCard padding="md">
      <h3 className="text-h3 font-semibold text-gray-900">Opportunity Breakdown</h3>
      <p className="mt-2 text-body text-gray-500">
        Recoverable ARR grouped by verification category.
      </p>
      <div className="mt-8 grid gap-4 md:grid-cols-2">
        {items.map((item) => (
          <GlassCard key={item.category} interactive padding="sm" subtle className="h-full">
            <p className="text-body font-medium text-gray-900">{item.label}</p>
            <p className="mt-3 text-h3 font-semibold tabular-nums text-gray-900">
              {formatCurrency(item.arr)}
            </p>
            <div className="mt-4 flex flex-wrap gap-4 text-small text-gray-500">
              <span>{item.issue_count} issues</span>
              {item.confidence && <span>{item.confidence}% confidence</span>}
              {item.account_count > 0 && <span>{item.account_count} accounts</span>}
            </div>
          </GlassCard>
        ))}
      </div>
    </GlassCard>
  );
}
