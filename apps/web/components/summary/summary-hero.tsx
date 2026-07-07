import type { ReactNode } from "react";

import { CountUp } from "@/components/count-up";
import { Reveal } from "@/components/motion";
import { formatCurrency, type FreeSummaryResponse } from "@rlr/shared";

interface SummaryHeroProps {
  summary: FreeSummaryResponse;
  headerAction?: ReactNode;
}

function parseArrForCountUp(value: string): {
  to: number;
  prefix: string;
  suffix: string;
  decimals: number;
} {
  const amount = Number.parseFloat(value);
  if (Number.isNaN(amount)) {
    return { to: 0, prefix: "$", suffix: "", decimals: 0 };
  }
  if (amount >= 1_000_000) {
    return { to: amount / 1_000_000, prefix: "$", suffix: "M", decimals: 2 };
  }
  if (amount >= 1_000) {
    return { to: amount / 1_000, prefix: "$", suffix: "K", decimals: 1 };
  }
  return { to: amount, prefix: "$", suffix: "", decimals: 0 };
}

export function SummaryHero({ summary, headerAction }: SummaryHeroProps) {
  const countUp = parseArrForCountUp(summary.recoverable_arr);
  const confidence = summary.confidence ? `${summary.confidence}%` : "-";

  const stats = [
    { label: "Confidence", value: confidence },
    {
      label: "Verification checks",
      value: `${summary.rules_completed}/${summary.rules_total}`,
    },
    { label: "Potential findings", value: String(summary.finding_count) },
    { label: "Accounts reviewed", value: String(summary.accounts_reviewed) },
    { label: "Invoices reviewed", value: String(summary.invoices_reviewed) },
  ];

  return (
    <section>
      <Reveal>
        <div className="flex flex-wrap items-center justify-between gap-4 pb-6">
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Free audit summary
          </p>
          {headerAction}
        </div>
      </Reveal>

      <Reveal delay={0.1}>
        <div className="mt-12 grid items-end gap-10 border-t border-line pt-12 md:grid-cols-[1.3fr_1fr]">
          <div>
            <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
              Total recoverable revenue
            </p>
            <div className="mt-4 font-heading text-[clamp(3rem,9vw,6rem)] leading-none tracking-tight tnum">
              <CountUp
                to={countUp.to}
                decimals={countUp.decimals}
                prefix={countUp.prefix}
                suffix={countUp.suffix}
              />
            </div>
            <p className="mt-5 max-w-md leading-relaxed text-muted-foreground">
              Identified across {summary.finding_count} distinct findings
              {summary.confidence ? `, at ${summary.confidence}% confidence` : ""}. The figure is
              annualized from your uploaded billing and CRM data.
            </p>
            <p className="mt-3 text-sm text-muted-foreground tnum">
              Exact: {formatCurrency(summary.recoverable_arr)}
            </p>
          </div>

          <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line">
            {stats.slice(0, 4).map((stat) => (
              <div key={stat.label} className="bg-card px-5 py-6">
                <dt className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  {stat.label}
                </dt>
                <dd className="mt-2 font-heading text-2xl tracking-tight tnum">{stat.value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </Reveal>
    </section>
  );
}
