'use client'

import { useEffect, useRef, useState } from 'react'
import { useInView } from 'motion/react'

/* Weighted count that eases to its value once in view. */
export function CountUp({
  to,
  duration = 1.8,
  prefix = '',
  suffix = '',
  decimals = 0,
  className,
}: {
  to: number
  duration?: number
  prefix?: string
  suffix?: string
  decimals?: number
  className?: string
}) {
  const ref = useRef<HTMLSpanElement>(null)
  const inView = useInView(ref, { once: true, margin: '-10% 0px' })
  const [value, setValue] = useState(0)

  useEffect(() => {
    if (!inView) return
    let raf = 0
    const start = performance.now()
    const ease = (t: number) => 1 - Math.pow(1 - t, 4)
    const tick = (now: number) => {
      const p = Math.min((now - start) / (duration * 1000), 1)
      setValue(to * ease(p))
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [inView, to, duration])

  const formatted = value.toLocaleString('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  })

  return (
    <span ref={ref} className={className}>
      {prefix}
      {formatted}
      {suffix}
    </span>
  )
}
