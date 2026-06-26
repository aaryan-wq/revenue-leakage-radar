import { GlassCard } from "@/components/ui/glass-card";
import type { SummaryCoverage } from "@rlr/shared";

interface CoverageSectionProps {
  coverage: SummaryCoverage;
}

function formatFileLabel(fileType: string): string {
  return fileType.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function CoverageSection({ coverage }: CoverageSectionProps) {
  return (
    <GlassCard padding="md">
      <h3 className="text-h3 font-semibold text-gray-900">Data Coverage</h3>
      <p className="mt-2 text-body text-gray-500">
        How complete your uploaded datasets are and how that affects verification confidence.
      </p>

      <div className="mt-8 grid gap-8 md:grid-cols-2">
        <div>
          <p className="text-overline uppercase text-gray-500">Billing Coverage</p>
          <p className="mt-2 text-small text-gray-600">
            Data tier: <span className="font-medium text-gray-900">{coverage.data_tier.replace(/_/g, " ")}</span>
          </p>
          {coverage.billing_files_uploaded.length > 0 && (
            <ul className="mt-4 space-y-2 text-small text-gray-700">
              {coverage.billing_files_uploaded.map((file) => (
                <li key={file} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-success" />
                  {formatFileLabel(file)}
                </li>
              ))}
            </ul>
          )}
          {coverage.billing_files_missing.length > 0 && (
            <ul className="mt-4 space-y-2 text-small text-gray-500">
              {coverage.billing_files_missing.map((file) => (
                <li key={file}>Missing recommended: {formatFileLabel(file)}</li>
              ))}
            </ul>
          )}
        </div>

        <div>
          <p className="text-overline uppercase text-gray-500">CRM Coverage</p>
          {coverage.crm_present ? (
            <ul className="mt-4 space-y-2 text-small text-gray-700">
              {coverage.crm_files_uploaded.map((file) => (
                <li key={file} className="flex items-center gap-2">
                  <span className="h-1.5 w-1.5 rounded-full bg-success" />
                  {formatFileLabel(file)}
                </li>
              ))}
            </ul>
          ) : (
            <p className="mt-4 text-small text-gray-500">No CRM exports uploaded.</p>
          )}
        </div>
      </div>

      <div className="mt-8 rounded-card border border-border bg-surface-glass-subtle p-5">
        <p className="text-overline uppercase text-gray-500">Confidence Impact</p>
        <p className="mt-2 text-body text-gray-700">{coverage.confidence_impact}</p>
      </div>
    </GlassCard>
  );
}
