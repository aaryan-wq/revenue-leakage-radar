'use client'

import { Reveal, Stagger, StaggerItem } from '../motion'

const steps = [
  {
    n: '01',
    title: 'Reconcile',
    body: 'We ingest exports from your billing, payment processor, and ledger, then align every transaction across systems, no integration required.',
  },
  {
    n: '02',
    title: 'Detect',
    body: 'Each revenue path is examined against its intended behavior. Where reality diverges from policy, we measure the gap and annualize the impact.',
  },
  {
    n: '03',
    title: 'Present',
    body: 'Findings arrive as a board-ready report: ranked by recoverable dollars, supported by evidence, and paired with a precise remedy.',
  },
]

export function Method() {
  return (
    <section className="mx-auto max-w-[78rem] px-6 py-28 md:px-10">
      <Reveal>
        <p className="mb-3 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          The method
        </p>
        <h2 className="max-w-2xl font-heading text-[clamp(1.9rem,4vw,3rem)] leading-[1.05] tracking-tight text-balance">
          Three deliberate movements, from raw export to recovered revenue.
        </h2>
      </Reveal>

      <Stagger className="mt-20 grid gap-x-12 gap-y-16 md:grid-cols-3">
        {steps.map((s) => (
          <StaggerItem key={s.n}>
            <div className="group">
              <div className="mb-6 flex items-baseline gap-4 border-t border-line pt-5">
                <span className="font-heading text-sm text-primary tnum">{s.n}</span>
                <span className="font-heading text-2xl tracking-tight">
                  {s.title}
                </span>
              </div>
              <p className="text-pretty leading-relaxed text-muted-foreground">
                {s.body}
              </p>
            </div>
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  )
}
