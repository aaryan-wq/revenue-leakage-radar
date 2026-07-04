'use client'

import Link from 'next/link'
import { findings, formatCurrency } from '@/lib/data'
import { Reveal, Stagger, StaggerItem, Magnetic } from '../motion'

export function LedgerPreview() {
  const rows = findings.slice(0, 5)
  return (
    <section className="border-t border-line bg-secondary/40">
      <div className="mx-auto max-w-[78rem] px-6 py-28 md:px-10">
        <Reveal>
          <div className="flex flex-wrap items-end justify-between gap-6">
            <div>
              <p className="mb-3 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                A recent engagement
              </p>
              <h2 className="max-w-xl font-heading text-[clamp(1.9rem,4vw,3rem)] leading-[1.05] tracking-tight text-balance">
                Seven findings. One quarter of recovery.
              </h2>
            </div>
            <Magnetic strength={0.25}>
              <Link
                href="/report"
                className="inline-flex items-center gap-2 rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem] transition-colors hover:bg-foreground hover:text-background"
              >
                Open full report →
              </Link>
            </Magnetic>
          </div>
        </Reveal>

        <Stagger className="mt-16">
          <div className="grid grid-cols-[1fr_auto] items-center gap-4 border-b border-line pb-3 text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground md:grid-cols-[auto_1fr_auto_auto]">
            <span className="hidden md:block">Ref</span>
            <span>Finding</span>
            <span className="hidden text-right md:block">Confidence</span>
            <span className="text-right">Annualized</span>
          </div>
          {rows.map((f) => (
            <StaggerItem key={f.id} y={14}>
              <div className="group grid grid-cols-[1fr_auto] items-center gap-4 border-b border-line py-5 transition-colors hover:bg-background md:grid-cols-[auto_1fr_auto_auto]">
                <span className="hidden font-mono text-xs text-muted-foreground md:block">
                  {f.id}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[0.98rem] text-foreground">
                    {f.title}
                  </p>
                  <p className="mt-0.5 text-xs uppercase tracking-wider text-muted-foreground">
                    {f.category}
                  </p>
                </div>
                <span className="hidden text-right text-sm text-muted-foreground tnum md:block">
                  {Math.round(f.confidence * 100)}%
                </span>
                <span className="text-right font-heading text-lg tracking-tight tnum">
                  {formatCurrency(f.annualized)}
                </span>
              </div>
            </StaggerItem>
          ))}
        </Stagger>
      </div>
    </section>
  )
}
