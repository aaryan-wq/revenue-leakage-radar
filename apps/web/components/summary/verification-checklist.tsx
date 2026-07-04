import { AlertTriangle, CheckCircle2, CircleDashed, Info, XCircle } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { formatCurrency, type VerificationCheckItem } from "@rlr/shared";

interface VerificationChecklistProps {
  checks: VerificationCheckItem[];
}

const STATUS_CONFIG = {
  passed: {
    label: "Passed",
    icon: CheckCircle2,
    className: "text-primary",
  },
  issues_found: {
    label: "Issues found",
    icon: AlertTriangle,
    className: "text-leak",
  },
  partial: {
    label: "Partial coverage",
    icon: Info,
    className: "text-muted-foreground",
  },
  not_run: {
    label: "Not run",
    icon: CircleDashed,
    className: "text-muted-foreground",
  },
  error: {
    label: "Error",
    icon: XCircle,
    className: "text-leak",
  },
} as const;

export function VerificationChecklist({ checks }: VerificationChecklistProps) {
  return (
    <section className="border-t border-line pt-12">
      <Reveal>
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Verification checks
        </p>
        <h3 className="mt-4 font-heading text-2xl tracking-tight text-foreground">
          Deterministic rules executed
        </h3>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
          Partial checks ran with reduced dataset coverage where noted.
        </p>
      </Reveal>

      <Stagger className="mt-10">
        {checks.map((check) => {
          const config = STATUS_CONFIG[check.status] ?? STATUS_CONFIG.not_run;
          const Icon = config.icon;
          const note = check.coverage_note ?? check.skip_reason;

          return (
            <StaggerItem key={check.rule_id} y={12}>
              <article className="grid gap-6 border-t border-line py-8 md:grid-cols-[1fr_auto_auto]">
                <div className="max-w-2xl">
                  <p className="font-heading text-lg tracking-tight text-foreground">{check.name}</p>
                  {note && <p className="mt-2 text-sm text-muted-foreground">{note}</p>}
                  <span
                    className={`mt-4 inline-flex items-center gap-2 text-[0.72rem] uppercase tracking-[0.14em] ${config.className}`}
                  >
                    <Icon className="h-4 w-4" strokeWidth={1.75} />
                    {config.label}
                  </span>
                </div>
                <div className="text-right md:min-w-[5rem]">
                  <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                    Findings
                  </p>
                  <p className="mt-2 font-heading text-xl tracking-tight tnum">{check.finding_count}</p>
                </div>
                <div className="text-right md:min-w-[8rem]">
                  <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                    Est. ARR
                  </p>
                  <p className="mt-2 font-heading text-xl tracking-tight tnum">
                    {formatCurrency(check.arr)}
                  </p>
                </div>
              </article>
            </StaggerItem>
          );
        })}
      </Stagger>
    </section>
  );
}
