'use client'

import { useRef, useState } from 'react'
import { motion, AnimatePresence } from 'motion/react'

const glide = [0.16, 1, 0.3, 1] as const

export interface UploadedFile {
  name: string
  size: string
  rows: string
}

const seeded: UploadedFile[] = [
  { name: 'billing_export_fy25.csv', size: '42.6 MB', rows: '1,204,882 rows' },
  { name: 'payments_ledger.csv', size: '38.1 MB', rows: '986,340 rows' },
]

export function UploadObject({
  onReady,
}: {
  onReady: (files: UploadedFile[]) => void
}) {
  const [hover, setHover] = useState(false)
  const [files, setFiles] = useState<UploadedFile[]>([])
  const inputRef = useRef<HTMLInputElement>(null)

  function ingest(list: FileList | null) {
    const next: UploadedFile[] =
      list && list.length
        ? Array.from(list).map((f) => ({
            name: f.name,
            size: `${(f.size / 1_048_576).toFixed(1)} MB`,
            rows: `${Math.round(f.size / 42).toLocaleString()} rows`,
          }))
        : seeded
    setFiles((prev) => [...prev, ...next])
  }

  return (
    <div>
      <motion.div
        onDragOver={(e) => {
          e.preventDefault()
          setHover(true)
        }}
        onDragLeave={() => setHover(false)}
        onDrop={(e) => {
          e.preventDefault()
          setHover(false)
          ingest(e.dataTransfer.files)
        }}
        onClick={() => inputRef.current?.click()}
        animate={{
          scale: hover ? 1.012 : 1,
          rotateX: hover ? -2 : 0,
        }}
        transition={{ type: 'spring', stiffness: 220, damping: 22 }}
        style={{ transformPerspective: 1200 }}
        className="group relative cursor-pointer overflow-hidden rounded-2xl border border-line bg-card"
      >
        {/* sweeping highlight on hover */}
        <motion.div
          className="pointer-events-none absolute inset-0"
          animate={{ opacity: hover ? 1 : 0 }}
          transition={{ duration: 0.6 }}
          style={{
            background:
              'radial-gradient(120% 80% at 50% 0%, color-mix(in oklch, var(--primary) 8%, transparent), transparent 60%)',
          }}
        />
        <div className="relative flex flex-col items-center px-8 py-20 text-center">
          <motion.div
            animate={{ y: hover ? -6 : 0 }}
            transition={{ type: 'spring', stiffness: 200, damping: 18 }}
            className="relative mb-8 flex h-20 w-20 items-center justify-center"
          >
            <motion.span
              className="absolute inset-0 rounded-2xl border border-primary/30"
              animate={{
                scale: hover ? [1, 1.18, 1] : 1,
                opacity: hover ? [0.6, 0, 0.6] : 0.4,
              }}
              transition={{ duration: 2, repeat: hover ? Infinity : 0 }}
            />
            <div className="flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10">
              <svg
                viewBox="0 0 24 24"
                className="h-7 w-7 text-primary"
                fill="none"
                stroke="currentColor"
                strokeWidth="1.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <path d="M12 16V4m0 0L7 9m5-5l5 5" />
                <path d="M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2" />
              </svg>
            </div>
          </motion.div>

          <h3 className="font-heading text-2xl tracking-tight">
            Place your data here
          </h3>
          <p className="mt-3 max-w-sm text-pretty leading-relaxed text-muted-foreground">
            Drop billing, payment, or ledger exports, or click to browse. CSV,
            XLSX, and JSON up to 2&nbsp;GB. Nothing leaves your environment
            unencrypted.
          </p>

          <input
            ref={inputRef}
            type="file"
            multiple
            className="hidden"
            onChange={(e) => ingest(e.target.files)}
          />
        </div>
      </motion.div>

      <AnimatePresence>
        {files.length > 0 && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.6, ease: glide }}
            className="mt-6 overflow-hidden"
          >
            <div className="rounded-xl border border-line bg-card">
              {files.map((f, i) => (
                <motion.div
                  key={f.name + i}
                  initial={{ opacity: 0, x: -12 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.5, ease: glide, delay: i * 0.06 }}
                  className="flex items-center gap-4 border-b border-line px-5 py-4 last:border-0"
                >
                  <span className="flex h-9 w-9 items-center justify-center rounded-md bg-primary/10 text-primary">
                    <svg
                      viewBox="0 0 24 24"
                      className="h-4 w-4"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="1.6"
                    >
                      <path d="M20 6L9 17l-5-5" />
                    </svg>
                  </span>
                  <div className="min-w-0 flex-1">
                    <p className="truncate text-sm text-foreground">{f.name}</p>
                    <p className="text-xs text-muted-foreground tnum">
                      {f.size} · {f.rows}
                    </p>
                  </div>
                  <span className="text-xs uppercase tracking-wider text-primary">
                    Validated
                  </span>
                </motion.div>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
