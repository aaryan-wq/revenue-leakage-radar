'use client'

import { useRouter } from 'next/navigation'
import { useState } from 'react'
import { motion } from 'motion/react'
import { SiteNav } from '@/components/site-nav'
import { UploadObject, type UploadedFile } from '@/components/upload/upload-object'
import { Magnetic } from '@/components/motion'

const glide = [0.16, 1, 0.3, 1] as const

const accepted = [
  { label: 'Billing exports', hint: 'Invoices, subscriptions, credits' },
  { label: 'Payment ledgers', hint: 'Charges, retries, refunds' },
  { label: 'Pricing records', hint: 'Quotes, discounts, approvals' },
]

export default function UploadPage() {
  const router = useRouter()
  const [files, setFiles] = useState<UploadedFile[]>([])

  return (
    <main className="min-h-screen">
      <SiteNav />
      <section className="mx-auto max-w-[64rem] px-6 pt-16 pb-28 md:px-10 md:pt-24">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: glide }}
        >
          <p className="mb-4 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Step one · Provide your data
          </p>
          <h1 className="max-w-2xl font-heading text-[clamp(2.1rem,5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
            Hand us the records. We&apos;ll find what&apos;s missing.
          </h1>
          <p className="mt-6 max-w-lg text-pretty leading-relaxed text-muted-foreground">
            The more systems you reconcile, the more precisely we can isolate
            leakage. Two files is enough to begin.
          </p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 1, ease: glide, delay: 0.15 }}
          className="mt-12 grid gap-10 lg:grid-cols-[1.4fr_1fr]"
        >
          <UploadObject onReady={setFiles} />

          <div className="flex flex-col">
            <p className="mb-5 text-[0.78rem] uppercase tracking-[0.16em] text-muted-foreground">
              What we accept
            </p>
            <div className="flex-1 space-y-px">
              {accepted.map((a) => (
                <div
                  key={a.label}
                  className="border-t border-line py-5 first:border-t-0"
                >
                  <p className="text-[0.98rem] text-foreground">{a.label}</p>
                  <p className="mt-1 text-sm text-muted-foreground">{a.hint}</p>
                </div>
              ))}
            </div>
            <div className="mt-6 rounded-xl border border-line bg-secondary/40 p-5">
              <p className="text-sm leading-relaxed text-muted-foreground">
                Files are processed in an isolated environment and never used to
                train models. You can revoke access at any time.
              </p>
            </div>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.3 }}
          className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-line pt-8"
        >
          <p className="text-sm text-muted-foreground tnum">
            {files.length > 0
              ? `${files.length} file${files.length > 1 ? 's' : ''} ready · validated`
              : 'Awaiting your first file'}
          </p>
          <Magnetic strength={0.3}>
            <button
              onClick={() => router.push('/processing')}
              className="inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
            >
              Begin analysis →
            </button>
          </Magnetic>
        </motion.div>
      </section>
    </main>
  )
}
