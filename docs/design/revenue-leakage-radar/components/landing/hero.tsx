'use client'

import { useRef, useState, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { motion, AnimatePresence } from 'motion/react'

const glide = [0.16, 1, 0.3, 1] as const

interface FileEntry {
  name: string
  size: string
}

function formatSize(bytes: number): string {
  if (bytes >= 1_073_741_824) return `${(bytes / 1_073_741_824).toFixed(1)} GB`
  if (bytes >= 1_048_576) return `${(bytes / 1_048_576).toFixed(1)} MB`
  return `${(bytes / 1024).toFixed(0)} KB`
}

const DEMO_FILE: FileEntry = {
  name: 'billing_export_fy25.csv',
  size: '42.6 MB',
}

export function Hero() {
  const [hover, setHover] = useState(false)
  const [files, setFiles] = useState<FileEntry[]>([])
  const [dragActive, setDragActive] = useState(false)
  const inputRef = useRef<HTMLInputElement>(null)
  const router = useRouter()

  const ingest = useCallback((list: FileList | null) => {
    if (!list || list.length === 0) {
      setFiles([DEMO_FILE])
      return
    }
    setFiles(Array.from(list).map((f) => ({ name: f.name, size: formatSize(f.size) })))
  }, [])

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault()
      setDragActive(false)
      setHover(false)
      ingest(e.dataTransfer.files)
    },
    [ingest],
  )

  const hasFiles = files.length > 0

  return (
    <section className="relative mx-auto max-w-[80rem] px-6 pt-20 pb-16 md:px-10 md:pt-28 md:pb-24">
      <div className="grid grid-cols-1 gap-12 lg:grid-cols-2 lg:gap-16 lg:items-center">

        {/* ── LEFT: Copy ── */}
        <div>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide }}
            className="mb-7 inline-flex items-center gap-2.5 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground"
          >
            <span className="h-px w-8 bg-primary/50" />
            Free instant audit
          </motion.p>

          <h1 className="font-heading text-[clamp(2.6rem,5.5vw,4.4rem)] leading-[0.95] tracking-tight text-balance">
            {['Drop your CSV.', 'See exactly where', 'revenue is leaking.'].map((line, i) => (
              <span key={i} className="block overflow-hidden">
                <motion.span
                  className="block"
                  initial={{ y: '110%' }}
                  animate={{ y: 0 }}
                  transition={{ duration: 1.1, ease: glide, delay: 0.08 + i * 0.12 }}
                >
                  {i === 1 ? <span className="italic text-primary">{line}</span> : line}
                </motion.span>
              </span>
            ))}
          </h1>

          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: glide, delay: 0.5 }}
            className="mt-7 text-pretty text-[1.05rem] leading-relaxed text-muted-foreground"
          >
            Upload any billing or payment export. Our engine reconciles every row
            and surfaces missed revenue, duplicate charges, and pricing drift, in
            under 90 seconds. No account needed.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide, delay: 0.65 }}
            className="mt-10 flex flex-wrap gap-x-8 gap-y-3"
          >
            {[
              ['2.4 B+', 'rows audited'],
              ['$340 M+', 'revenue recovered'],
              ['< 90 s', 'average runtime'],
            ].map(([val, label]) => (
              <div key={label}>
                <p className="font-heading text-2xl tracking-tight text-foreground tnum">{val}</p>
                <p className="text-[0.78rem] text-muted-foreground">{label}</p>
              </div>
            ))}
          </motion.div>
        </div>

        {/* ── RIGHT: Upload zone + CTA ── */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: glide, delay: 0.4 }}
          className="flex flex-col gap-4"
        >
          {/* Drop zone */}
          <motion.div
            onDragOver={(e) => { e.preventDefault(); setDragActive(true); setHover(true) }}
            onDragEnter={() => { setDragActive(true); setHover(true) }}
            onDragLeave={() => { setDragActive(false); setHover(false) }}
            onDrop={handleDrop}
            onClick={() => !hasFiles && inputRef.current?.click()}
            animate={{ scale: dragActive ? 1.008 : 1 }}
            transition={{ type: 'spring', stiffness: 260, damping: 24 }}
            className={[
              'relative overflow-hidden rounded-2xl border-2 transition-colors duration-300',
              hasFiles
                ? 'cursor-default border-primary/30 bg-card'
                : 'cursor-pointer border-dashed border-line bg-card hover:border-primary/40 hover:bg-card',
            ].join(' ')}
          >
            {/* Hover wash */}
            <motion.div
              className="pointer-events-none absolute inset-0"
              animate={{ opacity: hover && !hasFiles ? 1 : 0 }}
              transition={{ duration: 0.5 }}
              style={{
                background:
                  'radial-gradient(110% 80% at 50% 0%, color-mix(in oklch, var(--primary) 6%, transparent), transparent 60%)',
              }}
            />

            <AnimatePresence mode="wait">
              {!hasFiles ? (
                <motion.div
                  key="empty"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0, scale: 0.97 }}
                  transition={{ duration: 0.35 }}
                  className="relative flex flex-col items-center px-8 py-16 text-center"
                >
                  {/* Icon */}
                  <motion.div
                    animate={{ y: hover ? -5 : 0 }}
                    transition={{ type: 'spring', stiffness: 200, damping: 18 }}
                    className="relative mb-7 flex h-16 w-16 items-center justify-center"
                  >
                    <motion.span
                      className="absolute inset-0 rounded-xl border border-primary/25"
                      animate={{
                        scale: hover ? [1, 1.22, 1] : 1,
                        opacity: hover ? [0.5, 0, 0.5] : 0.3,
                      }}
                      transition={{ duration: 2, repeat: hover ? Infinity : 0 }}
                    />
                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                      <svg viewBox="0 0 24 24" className="h-6 w-6 text-primary" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M12 15V4m0 0L8 8m4-4l4 4" />
                        <path d="M4 17v2a1 1 0 0 0 1 1h14a1 1 0 0 0 1-1v-2" />
                      </svg>
                    </div>
                  </motion.div>

                  <p className="font-heading text-xl tracking-tight">
                    {dragActive ? 'Release to audit' : 'Drop your CSV or XLSX here'}
                  </p>
                  <p className="mt-2 text-sm text-muted-foreground">
                    or{' '}
                    <span className="underline underline-offset-2 decoration-primary/50 text-foreground/70">
                      click to browse
                    </span>
                    {' '},  up to 2 GB, any billing or payment export
                  </p>

                  <div className="mt-8 flex flex-wrap items-center justify-center gap-x-5 gap-y-2 text-[0.75rem] text-muted-foreground">
                    {['End-to-end encrypted', 'No account required', 'Results in <90 s'].map((t) => (
                      <span key={t} className="flex items-center gap-1.5">
                        <span className="h-1 w-1 rounded-full bg-primary/50" />
                        {t}
                      </span>
                    ))}
                  </div>
                </motion.div>
              ) : (
                <motion.div
                  key="files"
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.45, ease: glide }}
                  className="relative px-6 py-5"
                >
                  <div className="flex items-center justify-between pb-4 border-b border-line">
                    <p className="text-[0.78rem] uppercase tracking-[0.15em] text-muted-foreground">
                      {files.length} file{files.length > 1 ? 's' : ''} ready
                    </p>
                    <button
                      onClick={() => inputRef.current?.click()}
                      className="text-[0.78rem] text-primary underline underline-offset-2 decoration-primary/40 hover:decoration-primary/80 transition-colors"
                    >
                      Add more
                    </button>
                  </div>

                  {files.map((f, i) => (
                    <motion.div
                      key={f.name + i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.4, ease: glide, delay: i * 0.07 }}
                      className="flex items-center gap-4 py-4 border-b border-line last:border-0"
                    >
                      <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-primary/10">
                        <svg viewBox="0 0 24 24" className="h-4 w-4 text-primary" fill="none" stroke="currentColor" strokeWidth="1.8">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8l-6-6z" strokeLinejoin="round" />
                          <polyline points="14 2 14 8 20 8" strokeLinejoin="round" />
                        </svg>
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="truncate text-sm font-medium text-foreground">{f.name}</p>
                        <p className="text-xs text-muted-foreground tnum">{f.size}</p>
                      </div>
                      <span className="text-[0.72rem] font-medium uppercase tracking-wider text-primary">
                        Validated
                      </span>
                    </motion.div>
                  ))}
                </motion.div>
              )}
            </AnimatePresence>

            <input
              ref={inputRef}
              type="file"
              multiple
              accept=".csv,.xlsx,.json"
              className="hidden"
              onChange={(e) => ingest(e.target.files)}
            />
          </motion.div>

          {/* CTA row */}
          <div className="flex flex-wrap items-center gap-4">
            <motion.button
              onClick={() => router.push('/processing')}
              whileHover={{ scale: 1.025 }}
              whileTap={{ scale: 0.97 }}
              transition={{ type: 'spring', stiffness: 340, damping: 26 }}
              className={[
                'group relative inline-flex items-center gap-2.5 rounded-full px-7 py-4 text-[0.95rem] font-medium transition-shadow',
                hasFiles
                  ? 'bg-primary text-primary-foreground shadow-[0_12px_40px_-10px] shadow-primary/40 hover:shadow-[0_18px_55px_-12px] hover:shadow-primary/50'
                  : 'bg-primary/70 text-primary-foreground cursor-default',
              ].join(' ')}
            >
              {hasFiles ? 'Run free audit' : 'Upload a file to begin'}
              {hasFiles && (
                <span className="transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:translate-x-1">
                  →
                </span>
              )}
            </motion.button>

            <p className="text-[0.82rem] text-muted-foreground">
              {hasFiles
                ? 'Your file is processed locally. Nothing is stored.'
                : (
                  <>
                    No real data?{' '}
                    <button
                      onClick={() => ingest(null)}
                      className="underline underline-offset-2 text-foreground/60 hover:text-foreground transition-colors"
                    >
                      Load sample file
                    </button>
                  </>
                )}
            </p>
          </div>
        </motion.div>

      </div>
    </section>
  )
}
