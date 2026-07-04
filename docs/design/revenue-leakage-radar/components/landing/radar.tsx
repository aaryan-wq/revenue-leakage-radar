'use client'

import { motion } from 'motion/react'

const blips = [
  { x: 30, y: 28, r: 5, delay: 0.2 },
  { x: 72, y: 40, r: 3.5, delay: 1.1 },
  { x: 58, y: 70, r: 6.5, delay: 0.6 },
  { x: 24, y: 62, r: 3, delay: 1.6 },
  { x: 80, y: 74, r: 4, delay: 2.1 },
]

/* A precision instrument, concentric rings with a slow, weighted sweep.
   Blips surface where revenue is leaking. */
export function Radar() {
  return (
    <div className="relative aspect-square w-full">
      <svg
        viewBox="0 0 100 100"
        className="h-full w-full overflow-visible"
        aria-hidden="true"
      >
        <defs>
          <radialGradient id="sweep" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.28" />
            <stop offset="70%" stopColor="var(--primary)" stopOpacity="0.05" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
          </radialGradient>
          <linearGradient id="ray" x1="50%" y1="50%" x2="100%" y2="50%">
            <stop offset="0%" stopColor="var(--primary)" stopOpacity="0.5" />
            <stop offset="100%" stopColor="var(--primary)" stopOpacity="0" />
          </linearGradient>
        </defs>

        {[46, 34, 22, 10].map((r) => (
          <circle
            key={r}
            cx="50"
            cy="50"
            r={r}
            fill="none"
            stroke="var(--line)"
            strokeWidth="0.3"
          />
        ))}
        <line x1="4" y1="50" x2="96" y2="50" stroke="var(--line)" strokeWidth="0.3" />
        <line x1="50" y1="4" x2="50" y2="96" stroke="var(--line)" strokeWidth="0.3" />

        {/* sweeping wedge */}
        <motion.g
          style={{ originX: '50px', originY: '50px' }}
          animate={{ rotate: 360 }}
          transition={{ duration: 7, repeat: Infinity, ease: 'linear' }}
        >
          <path d="M50 50 L96 50 A46 46 0 0 1 78 88 Z" fill="url(#sweep)" />
          <line x1="50" y1="50" x2="96" y2="50" stroke="url(#ray)" strokeWidth="0.6" />
        </motion.g>

        {/* leak blips */}
        {blips.map((b, i) => (
          <g key={i}>
            <motion.circle
              cx={b.x}
              cy={b.y}
              r={b.r}
              fill="var(--leak)"
              fillOpacity="0.18"
              animate={{ scale: [1, 2.1, 1], opacity: [0.5, 0, 0.5] }}
              transition={{
                duration: 3.2,
                repeat: Infinity,
                delay: b.delay,
                ease: 'easeOut',
              }}
              style={{ originX: `${b.x}px`, originY: `${b.y}px` }}
            />
            <circle cx={b.x} cy={b.y} r="1.1" fill="var(--leak)" />
          </g>
        ))}

        <circle cx="50" cy="50" r="1.6" fill="var(--primary)" />
      </svg>
    </div>
  )
}
