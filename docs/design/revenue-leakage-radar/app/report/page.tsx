import Link from 'next/link'
import { SiteNav } from '@/components/site-nav'
import { SiteFooter } from '@/components/site-footer'
import { Reveal, Stagger, StaggerItem } from '@/components/motion'
import { CountUp } from '@/components/count-up'
import { CategoryBars } from '@/components/report/category-bars'
import {
  company,
  totals,
  findings,
  formatCurrency,
  type Severity,
} from '@/lib/data'

const severityLabel: Record<Severity, string> = {
  critical: 'Critical',
  elevated: 'Elevated',
  monitor: 'Monitor',
}

const severityClass: Record<Severity, string> = {
  critical: 'text-leak',
  elevated: 'text-primary',
  monitor: 'text-muted-foreground',
}

export default function ReportPage() {
  return (
    <main className="min-h-screen">
      <SiteNav />

      {/* Cover */}
      <section className="mx-auto max-w-[68rem] px-6 pt-16 pb-20 md:px-10 md:pt-24">
        <Reveal>
          <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            <span>Confidential</span>
            <span className="h-1 w-1 rounded-full bg-muted-foreground/50" />
            <span>{company.name}</span>
            <span className="h-1 w-1 rounded-full bg-muted-foreground/50" />
            <span>{company.period}</span>
          </div>
          <h1 className="mt-8 max-w-3xl font-heading text-[clamp(2.4rem,6vw,4.4rem)] leading-[0.98] tracking-tight text-balance">
            Revenue Leakage Findings
          </h1>
          <p className="mt-7 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
            An examination of {company.scope.toLowerCase()}, isolating the
            recoverable revenue lost to billing, pricing, and payment failures
            over the reporting period.
          </p>
        </Reveal>

        {/* Headline figure */}
        <Reveal delay={0.15}>
          <div className="mt-16 grid items-end gap-10 border-t border-line pt-12 md:grid-cols-[1.3fr_1fr]">
            <div>
              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Total recoverable revenue
              </p>
              <div className="mt-4 font-heading text-[clamp(3rem,9vw,6rem)] leading-none tracking-tight tnum">
                <CountUp to={4.18} decimals={2} prefix="$" suffix="M" />
              </div>
              <p className="mt-5 max-w-md leading-relaxed text-muted-foreground">
                Identified across {totals.findings} distinct findings, at a
                median confidence of {Math.round(totals.confidence * 100)}%. The
                figure is annualized and net of remediation effort.
              </p>
            </div>
            <dl className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line">
              {[
                { k: 'Examined', v: formatCurrency(totals.examined, { compact: true }) },
                { k: 'Findings', v: String(totals.findings) },
                { k: 'Confidence', v: `${Math.round(totals.confidence * 100)}%` },
                { k: 'Leakage rate', v: '1.34%' },
              ].map((s) => (
                <div key={s.k} className="bg-card px-5 py-6">
                  <dt className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    {s.k}
                  </dt>
                  <dd className="mt-2 font-heading text-2xl tracking-tight tnum">
                    {s.v}
                  </dd>
                </div>
              ))}
            </dl>
          </div>
        </Reveal>
      </section>

      {/* Distribution */}
      <section className="border-y border-line bg-secondary/30">
        <div className="mx-auto grid max-w-[68rem] gap-14 px-6 py-20 md:grid-cols-[0.9fr_1.1fr] md:px-10">
          <Reveal>
            <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
              Where it leaks
            </p>
            <h2 className="mt-4 font-heading text-[clamp(1.7rem,3.5vw,2.6rem)] leading-[1.05] tracking-tight text-balance">
              Concentration of loss by revenue function.
            </h2>
            <p className="mt-5 leading-relaxed text-muted-foreground">
              Payments and pricing account for the majority of recoverable
              revenue. Addressing the two critical findings alone captures over
              sixty percent of the total.
            </p>
          </Reveal>
          <Reveal delay={0.1}>
            <CategoryBars />
          </Reveal>
        </div>
      </section>

      {/* Findings ledger */}
      <section className="mx-auto max-w-[68rem] px-6 py-24 md:px-10">
        <Reveal>
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            The findings
          </p>
          <h2 className="mt-4 max-w-xl font-heading text-[clamp(1.7rem,3.5vw,2.6rem)] leading-[1.05] tracking-tight text-balance">
            Each finding, ranked by recoverable impact.
          </h2>
        </Reveal>

        <Stagger className="mt-16">
          {findings.map((f, i) => (
            <StaggerItem key={f.id} y={16}>
              <article className="grid gap-8 border-t border-line py-12 md:grid-cols-[auto_1fr_auto]">
                <div className="flex items-start gap-4">
                  <span className="font-mono text-xs text-muted-foreground">
                    {f.id}
                  </span>
                </div>
                <div className="max-w-2xl">
                  <div className="mb-3 flex flex-wrap items-center gap-3">
                    <span
                      className={`text-[0.72rem] uppercase tracking-[0.14em] ${severityClass[f.severity]}`}
                    >
                      {severityLabel[f.severity]}
                    </span>
                    <span className="h-1 w-1 rounded-full bg-muted-foreground/40" />
                    <span className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                      {f.category}
                    </span>
                  </div>
                  <h3 className="font-heading text-2xl leading-snug tracking-tight text-balance">
                    {f.title}
                  </h3>
                  <p className="mt-4 leading-relaxed text-muted-foreground">
                    {f.detail}
                  </p>

                  <div className="mt-7 flex flex-wrap gap-x-10 gap-y-3">
                    {f.evidence.map((e) => (
                      <div key={e.label}>
                        <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                          {e.label}
                        </p>
                        <p className="mt-1 text-sm text-foreground tnum">
                          {e.value}
                        </p>
                      </div>
                    ))}
                  </div>

                  <div className="mt-7 border-l-2 border-primary/40 pl-4">
                    <p className="text-[0.72rem] uppercase tracking-[0.12em] text-primary">
                      Recommended remedy
                    </p>
                    <p className="mt-1.5 leading-relaxed text-foreground">
                      {f.recovery}
                    </p>
                  </div>
                </div>
                <div className="text-right md:min-w-[10rem]">
                  <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                    Annualized
                  </p>
                  <p className="mt-2 font-heading text-3xl tracking-tight tnum">
                    {formatCurrency(f.annualized)}
                  </p>
                  <p className="mt-3 text-xs text-muted-foreground tnum">
                    {f.instances.toLocaleString()} instances ·{' '}
                    {Math.round(f.confidence * 100)}% conf.
                  </p>
                </div>
              </article>
            </StaggerItem>
          ))}
        </Stagger>

        <Reveal>
          <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-10">
            <p className="max-w-md text-sm leading-relaxed text-muted-foreground">
              Prepared by Revenue Leakage Radar. Figures are estimates derived
              from the supplied data and intended for internal review.
            </p>
            <Link
              href="/workspace"
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
            >
              Open the workspace →
            </Link>
          </div>
        </Reveal>
      </section>

      <SiteFooter />
    </main>
  )
}
