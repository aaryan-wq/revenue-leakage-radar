import { SiteNav } from '@/components/site-nav'
import { SiteFooter } from '@/components/site-footer'
import { Hero } from '@/components/landing/hero'
import { Method } from '@/components/landing/method'
import { LedgerPreview } from '@/components/landing/ledger-preview'
import { Reveal } from '@/components/motion'
import { CountUp } from '@/components/count-up'

const stats = [
  { value: 312, prefix: '$', suffix: 'M', decimals: 0, label: 'Transaction value examined' },
  { value: 11, prefix: '', suffix: '', decimals: 0, label: 'Source systems reconciled' },
  { value: 94, prefix: '', suffix: '%', decimals: 0, label: 'Median finding confidence' },
  { value: 9, prefix: '', suffix: ' days', decimals: 0, label: 'Average time to recovery' },
]

export default function Page() {
  return (
    <main className="min-h-screen">
      <SiteNav />
      <Hero />

      <section className="border-y border-line">
        <div className="mx-auto grid max-w-[78rem] grid-cols-2 gap-px bg-line md:grid-cols-4">
          {stats.map((s, i) => (
            <Reveal
              key={s.label}
              delay={i * 0.08}
              className="bg-background px-6 py-10 md:px-10"
            >
              <div className="font-heading text-3xl tracking-tight tnum md:text-4xl">
                <CountUp
                  to={s.value}
                  prefix={s.prefix}
                  suffix={s.suffix}
                  decimals={s.decimals}
                />
              </div>
              <p className="mt-3 text-[0.82rem] leading-relaxed text-muted-foreground">
                {s.label}
              </p>
            </Reveal>
          ))}
        </div>
      </section>

      <Method />
      <LedgerPreview />
      <SiteFooter />
    </main>
  )
}
