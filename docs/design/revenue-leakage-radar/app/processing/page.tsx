'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'motion/react'
import { SiteNav } from '@/components/site-nav'

const glide = [0.16, 1, 0.3, 1] as const

const phases = [
  { label: 'Reconciling transactions', detail: 'Aligning 4.2M records across 11 systems' },
  { label: 'Mapping revenue paths', detail: 'Tracing intended billing behavior' },
  { label: 'Detecting divergence', detail: 'Comparing reality against policy' },
  { label: 'Annualizing impact', detail: 'Quantifying recoverable dollars' },
  { label: 'Composing report', detail: 'Ranking findings by confidence' },
]

export default function ProcessingPage() {
  const router = useRouter()
  const [phase, setPhase] = useState(0)
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const total = 9000
    const start = performance.now()
    let raf = 0
    const tick = (now: number) => {
      const p = Math.min((now - start) / total, 1)
      setProgress(p)
      setPhase(Math.min(Math.floor(p * phases.length), phases.length - 1))
      if (p < 1) raf = requestAnimationFrame(tick)
      else setTimeout(() => router.push('/report'), 900)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [router])

  return (
    <main className="min-h-screen">
      <SiteNav />
      <section className="mx-auto flex min-h-[calc(100vh-4rem)] max-w-[60rem] flex-col items-center justify-center px-6 py-16 md:px-10">
        {/* Instrument */}
        <div className="relative mb-16 h-56 w-56">
          <svg viewBox="0 0 200 200" className="h-full w-full -rotate-90">
            <circle
              cx="100"
              cy="100"
              r="88"
              fill="none"
              stroke="var(--line)"
              strokeWidth="1"
            />
            <motion.circle
              cx="100"
              cy="100"
              r="88"
              fill="none"
              stroke="var(--primary)"
              strokeWidth="2"
              strokeLinecap="round"
              strokeDasharray={2 * Math.PI * 88}
              animate={{
                strokeDashoffset: 2 * Math.PI * 88 * (1 - progress),
              }}
              transition={{ ease: 'linear' }}
            />
          </svg>
          {/* concentric breathing rings */}
          {[64, 44, 26].map((r, i) => (
            <motion.span
              key={r}
              className="absolute left-1/2 top-1/2 rounded-full border border-primary/20"
              style={{
                width: r * 2,
                height: r * 2,
                marginLeft: -r,
                marginTop: -r,
              }}
              animate={{ scale: [1, 1.08, 1], opacity: [0.5, 0.2, 0.5] }}
              transition={{
                duration: 2.6,
                repeat: Infinity,
                delay: i * 0.3,
                ease: 'easeInOut',
              }}
            />
          ))}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="font-heading text-4xl tracking-tight tnum">
              {Math.round(progress * 100)}%
            </span>
            <span className="mt-1 text-[0.7rem] uppercase tracking-[0.18em] text-muted-foreground">
              Analyzing
            </span>
          </div>
        </div>

        <div className="h-16 text-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={phase}
              initial={{ opacity: 0, y: 12, filter: 'blur(6px)' }}
              animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
              exit={{ opacity: 0, y: -12, filter: 'blur(6px)' }}
              transition={{ duration: 0.6, ease: glide }}
            >
              <p className="font-heading text-2xl tracking-tight">
                {phases[phase].label}
              </p>
              <p className="mt-2 text-sm text-muted-foreground">
                {phases[phase].detail}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* phase ticks */}
        <div className="mt-12 flex items-center gap-2.5">
          {phases.map((_, i) => (
            <motion.span
              key={i}
              className="h-1 rounded-full"
              animate={{
                width: i === phase ? 36 : 8,
                backgroundColor:
                  i <= phase ? 'var(--primary)' : 'var(--line)',
              }}
              transition={{ type: 'spring', stiffness: 260, damping: 26 }}
            />
          ))}
        </div>

        <p className="mt-12 max-w-sm text-center text-sm leading-relaxed text-muted-foreground">
          This usually takes under a minute. We&apos;re being thorough so the
          findings are ones you can stand behind.
        </p>
      </section>
    </main>
  )
}
