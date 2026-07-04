'use client'

import { motion } from 'motion/react'
import { categories, formatCurrency } from '@/lib/data'

const glide = [0.16, 1, 0.3, 1] as const

export function CategoryBars() {
  const max = Math.max(...categories.map((c) => c.amount))
  return (
    <div className="space-y-7">
      {categories.map((c, i) => (
        <div key={c.name}>
          <div className="mb-2.5 flex items-baseline justify-between">
            <span className="text-[0.95rem] text-foreground">{c.name}</span>
            <span className="font-heading text-lg tracking-tight tnum">
              {formatCurrency(c.amount)}
            </span>
          </div>
          <div className="h-px w-full bg-line">
            <motion.div
              className="h-px bg-primary"
              initial={{ scaleX: 0 }}
              whileInView={{ scaleX: c.amount / max }}
              viewport={{ once: true }}
              transition={{ duration: 1.2, ease: glide, delay: i * 0.1 }}
              style={{ originX: 0 }}
            />
          </div>
        </div>
      ))}
    </div>
  )
}
