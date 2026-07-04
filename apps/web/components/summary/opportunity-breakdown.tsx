import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { GlassCard } from "@/components/ui/glass-card";
import { formatCurrency, type OpportunityBreakdownItem } from "@rlr/shared";

interface OpportunityBreakdownProps {
  items: OpportunityBreakdownItem[];
}

export function OpportunityBreakdown({ items }: OpportunityBreakdownProps) {
  if (items.length === 0) {
    return (
      <Reveal>
        <section className="border-t border-line pt-12">
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Opportunity breakdown
          </p>
          <h3 className="mt-4 font-heading text-2xl tracking-tight text-foreground">
            No recoverable opportunities identified
          </h3>
          <p className="mt-3 text-sm text-muted-foreground">
            Verification checks did not surface material leakage in the uploaded datasets.
          </p>
        </section>
      </Reveal>
    );
  }

  return (
    <section className="border-y border-line bg-secondary/30">
      <div className="py-16">
        <Reveal>
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Where it leaks
          </p>
          <h3 className="mt-4 font-heading text-[clamp(1.7rem,3.5vw,2.6rem)] leading-[1.05] tracking-tight text-balance">
            Recoverable ARR by verification category
          </h3>
          <p className="mt-4 max-w-xl leading-relaxed text-muted-foreground">
            Grouped by the deterministic rules that surfaced each opportunity.
          </p>
        </Reveal>

        <Stagger className="mt-12 grid gap-4 md:grid-cols-2">
          {items.map((item) => (
            <StaggerItem key={item.category}>
              <GlassCard padding="sm" subtle className="h-full">
                <p className="text-sm font-medium text-foreground">{item.label}</p>
                <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                  {formatCurrency(item.arr)}
                </p>
                <div className="mt-4 flex flex-wrap gap-x-6 gap-y-2 text-sm text-muted-foreground">
                  <span className="tnum">{item.issue_count} issues</span>
                  {item.confidence && <span className="tnum">{item.confidence}% confidence</span>}
                  {item.account_count > 0 && (
                    <span className="tnum">{item.account_count} accounts</span>
                  )}
                </div>
              </GlassCard>
            </StaggerItem>
          ))}
        </Stagger>
      </div>
    </section>
  );
}
