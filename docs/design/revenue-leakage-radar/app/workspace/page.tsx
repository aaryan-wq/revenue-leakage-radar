import { SiteNav } from '@/components/site-nav'
import { WorkspaceView } from '@/components/workspace/workspace-view'
import { Reveal } from '@/components/motion'
import { CountUp } from '@/components/count-up'
import { company, totals, formatCurrency } from '@/lib/data'

export default function WorkspacePage() {
  return (
    <main className="min-h-screen">
      <SiteNav />

      <section className="mx-auto max-w-[78rem] px-6 pt-14 md:px-10 md:pt-20">
        <Reveal>
          <div className="flex flex-wrap items-end justify-between gap-8">
            <div>
              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Audit workspace · {company.name}
              </p>
              <h1 className="mt-4 font-heading text-[clamp(2rem,4.5vw,3.2rem)] leading-[1.02] tracking-tight text-balance">
                Work through the findings.
              </h1>
            </div>
            <div className="text-right">
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                Open recovery
              </p>
              <div className="mt-2 font-heading text-3xl tracking-tight tnum md:text-4xl">
                <CountUp to={4.18} decimals={2} prefix="$" suffix="M" />
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      <section className="mx-auto mt-10 max-w-[78rem] px-6 pb-24 md:px-10">
        <Reveal delay={0.1}>
          <div className="overflow-hidden rounded-2xl border border-line bg-card">
            <WorkspaceView />
          </div>
        </Reveal>

        <Reveal delay={0.15}>
          <p className="mt-6 text-center text-sm text-muted-foreground tnum">
            {totals.findings} findings · {formatCurrency(totals.examined, { compact: true })}{' '}
            examined · {Math.round(totals.confidence * 100)}% median confidence
          </p>
        </Reveal>
      </section>
    </main>
  )
}
