import { Reveal } from "@/components/motion";
import { GlassCard } from "@/components/ui/glass-card";
import type { SummaryCoverage } from "@rlr/shared";

interface CoverageSectionProps {
  coverage: SummaryCoverage;
}

function formatFileLabel(fileType: string): string {
  return fileType.replace(/_/g, " ").replace(/\b\w/g, (character) => character.toUpperCase());
}

export function CoverageSection({ coverage }: CoverageSectionProps) {
  return (
    <section className="border-t border-line pt-12">
      <Reveal>
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Data coverage
        </p>
        <h3 className="mt-4 font-heading text-2xl tracking-tight text-foreground">
          How complete your datasets are
        </h3>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
          Upload breadth affects which verification rules can run and overall confidence.
        </p>
      </Reveal>

      <div className="mt-10 grid gap-10 md:grid-cols-2">
        <Reveal delay={0.08}>
          <GlassCard padding="sm" subtle>
            <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
              Billing coverage
            </p>
            <p className="mt-3 text-sm text-muted-foreground">
              Data tier:{" "}
              <span className="font-medium text-foreground">
                {coverage.data_tier.replace(/_/g, " ")}
              </span>
            </p>
            {coverage.billing_files_uploaded.length > 0 && (
              <ul className="mt-4 space-y-2 text-sm text-foreground">
                {coverage.billing_files_uploaded.map((file) => (
                  <li key={file} className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    {formatFileLabel(file)}
                  </li>
                ))}
              </ul>
            )}
            {coverage.billing_files_missing.length > 0 && (
              <ul className="mt-4 space-y-2 text-sm text-muted-foreground">
                {coverage.billing_files_missing.map((file) => (
                  <li key={file}>Missing recommended: {formatFileLabel(file)}</li>
                ))}
              </ul>
            )}
          </GlassCard>
        </Reveal>

        <Reveal delay={0.12}>
          <GlassCard padding="sm" subtle>
            <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
              CRM coverage
            </p>
            {coverage.crm_present ? (
              <ul className="mt-4 space-y-2 text-sm text-foreground">
                {coverage.crm_files_uploaded.map((file) => (
                  <li key={file} className="flex items-center gap-2">
                    <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                    {formatFileLabel(file)}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="mt-4 text-sm text-muted-foreground">No CRM exports uploaded.</p>
            )}
          </GlassCard>
        </Reveal>
      </div>

      <Reveal delay={0.16}>
        <GlassCard padding="sm" className="mt-8 border-line bg-card">
          <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
            Confidence impact
          </p>
          <p className="mt-3 text-sm leading-relaxed text-foreground">{coverage.confidence_impact}</p>
        </GlassCard>
      </Reveal>
    </section>
  );
}
