'use client'

import { useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'
import { findings, formatCurrency, type Severity } from '@/lib/data'
import { CountUp } from '../count-up'

const glide = [0.16, 1, 0.3, 1] as const

const severityDot: Record<Severity, string> = {
  critical: 'bg-leak',
  elevated: 'bg-primary',
  monitor: 'bg-muted-foreground/50',
}

const severityText: Record<Severity, string> = {
  critical: 'Critical',
  elevated: 'Elevated',
  monitor: 'Monitor',
}

export function WorkspaceView() {
  const [activeId, setActiveId] = useState(findings[0].id)
  const active = findings.find((f) => f.id === activeId)!

  return (
    <div className="grid gap-0 lg:grid-cols-[20rem_1fr]">
      {/* Index rail */}
      <aside className="border-b border-line lg:border-b-0 lg:border-r">
        <div className="px-6 py-6 md:px-8">
          <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
            Findings · {findings.length}
          </p>
        </div>
        <nav className="pb-4">
          {findings.map((f) => {
            const selected = f.id === activeId
            return (
              <button
                key={f.id}
                onClick={() => setActiveId(f.id)}
                className="relative block w-full px-6 py-4 text-left md:px-8"
              >
                {selected && (
                  <motion.span
                    layoutId="ws-active"
                    className="absolute inset-y-1 left-0 w-[2px] bg-primary"
                    transition={{ type: 'spring', stiffness: 320, damping: 30 }}
                  />
                )}
                <div className="flex items-start gap-3">
                  <span
                    className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${severityDot[f.severity]}`}
                  />
                  <div className="min-w-0 flex-1">
                    <p
                      className={`truncate text-[0.9rem] transition-colors ${
                        selected ? 'text-foreground' : 'text-muted-foreground'
                      }`}
                    >
                      {f.title}
                    </p>
                    <p className="mt-0.5 text-xs text-muted-foreground tnum">
                      {f.id} · {formatCurrency(f.annualized, { compact: true })}
                    </p>
                  </div>
                </div>
              </button>
            )
          })}
        </nav>
      </aside>

      {/* Detail surface */}
      <section className="min-h-[40rem] px-6 py-10 md:px-12 md:py-14">
        <AnimatePresence mode="wait">
          <motion.div
            key={active.id}
            initial={{ opacity: 0, y: 16, filter: 'blur(6px)' }}
            animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
            exit={{ opacity: 0, y: -10, filter: 'blur(6px)' }}
            transition={{ duration: 0.6, ease: glide }}
          >
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-xs text-muted-foreground">
                {active.id}
              </span>
              <span className="flex items-center gap-2 text-[0.72rem] uppercase tracking-[0.14em]">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${severityDot[active.severity]}`}
                />
                {severityText[active.severity]}
              </span>
              <span className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                {active.category}
              </span>
            </div>

            <h2 className="mt-5 max-w-2xl font-heading text-[clamp(1.8rem,4vw,2.8rem)] leading-[1.05] tracking-tight text-balance">
              {active.title}
            </h2>

            {/* Dominant figure */}
            <div className="mt-10 flex flex-wrap items-end gap-x-14 gap-y-8 border-y border-line py-10">
              <div>
                <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  Recoverable, annualized
                </p>
                <div className="mt-3 font-heading text-[clamp(2.6rem,6vw,4.4rem)] leading-none tracking-tight tnum">
                  <CountUp
                    key={active.id}
                    to={active.annualized}
                    prefix="$"
                    duration={1.4}
                  />
                </div>
              </div>
              <div className="flex gap-x-12 gap-y-6">
                <div>
                  <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Instances
                  </p>
                  <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                    {active.instances.toLocaleString()}
                  </p>
                </div>
                <div>
                  <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Confidence
                  </p>
                  <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                    {Math.round(active.confidence * 100)}%
                  </p>
                </div>
              </div>
            </div>

            <p className="mt-10 max-w-2xl text-lg leading-relaxed text-muted-foreground">
              {active.detail}
            </p>

            {/* Evidence grid */}
            <div className="mt-10">
              <p className="mb-5 text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                Evidence
              </p>
              <div className="grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-3">
                {active.evidence.map((e) => (
                  <div key={e.label} className="bg-card px-5 py-6">
                    <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                      {e.label}
                    </p>
                    <p className="mt-2 font-heading text-xl tracking-tight tnum">
                      {e.value}
                    </p>
                  </div>
                ))}
              </div>
            </div>

            <div className="mt-10 max-w-2xl border-l-2 border-primary/40 pl-5">
              <p className="text-[0.72rem] uppercase tracking-[0.12em] text-primary">
                Recommended remedy
              </p>
              <p className="mt-2 text-lg leading-relaxed text-foreground">
                {active.recovery}
              </p>
            </div>

            <div className="mt-10 flex flex-wrap gap-3">
              <motion.button
                whileTap={{ scale: 0.96 }}
                transition={{ type: 'spring', stiffness: 400, damping: 26 }}
                className="rounded-full bg-primary px-5 py-2.5 text-[0.85rem] font-medium text-primary-foreground"
              >
                Assign owner
              </motion.button>
              <motion.button
                whileTap={{ scale: 0.96 }}
                transition={{ type: 'spring', stiffness: 400, damping: 26 }}
                className="rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem] transition-colors hover:bg-secondary"
              >
                Mark in progress
              </motion.button>
              <motion.button
                whileTap={{ scale: 0.96 }}
                transition={{ type: 'spring', stiffness: 400, damping: 26 }}
                className="rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem] transition-colors hover:bg-secondary"
              >
                Export evidence
              </motion.button>
            </div>
          </motion.div>
        </AnimatePresence>
      </section>
    </div>
  )
}
