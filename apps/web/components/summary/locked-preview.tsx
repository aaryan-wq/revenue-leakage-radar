import { Lock } from "lucide-react";

import { GlassCard } from "@/components/ui/glass-card";
import { formatCurrency, type LockedPreviewItem } from "@rlr/shared";

interface LockedPreviewProps {
  items: LockedPreviewItem[];
}

export function LockedPreview({ items }: LockedPreviewProps) {
  if (items.length === 0) return null;

  return (
    <GlassCard padding="md">
      <div className="flex items-center gap-3">
        <Lock className="h-5 w-5 text-gray-400" strokeWidth={1.75} />
        <h3 className="text-h3 font-semibold text-gray-900">Detailed Findings Preview</h3>
      </div>
      <p className="mt-2 text-body text-gray-500">
        Unlock the full report to view customer names, invoice evidence, and remediation steps.
      </p>
      <div className="mt-8 grid gap-4 md:grid-cols-3">
        {items.map((item, index) => (
          <div
            key={`${item.category}-${index}`}
            className="glass-subtle relative overflow-hidden rounded-card p-6"
          >
            <div className="select-none blur-sm">
              <p className="text-body font-medium text-gray-900">{item.title}</p>
              <p className="mt-2 text-small text-gray-500">{item.category_label}</p>
              <p className="mt-4 text-h4 font-semibold tabular-nums text-gray-900">
                {formatCurrency(item.arr)}
              </p>
              <p className="mt-4 text-small text-gray-400">Customer names hidden</p>
              <p className="text-small text-gray-400">Invoice evidence hidden</p>
            </div>
            <div className="absolute inset-0 flex items-center justify-center bg-surface-glass/60 backdrop-blur-sm">
              <Lock className="h-6 w-6 text-gray-400" strokeWidth={1.75} />
            </div>
          </div>
        ))}
      </div>
    </GlassCard>
  );
}
