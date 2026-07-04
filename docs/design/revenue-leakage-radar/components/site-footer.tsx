'use client'

import Link from 'next/link'
import { Reveal, Magnetic } from './motion'

export function SiteFooter() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto max-w-[78rem] px-6 py-24 md:px-10">
        <Reveal>
          <div className="flex flex-col items-start justify-between gap-12 md:flex-row md:items-end">
            <div className="max-w-xl">
              <h2 className="font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
                Find out what your business is quietly leaving behind.
              </h2>
              <p className="mt-6 leading-relaxed text-muted-foreground">
                Your first audit takes minutes to begin and pays for itself in
                the first finding.
              </p>
              <Magnetic strength={0.3}>
                <Link
                  href="/upload"
                  className="mt-8 inline-flex items-center gap-2 rounded-full bg-primary px-6 py-3.5 text-[0.92rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
                >
                  Begin your audit →
                </Link>
              </Magnetic>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-primary" />
              Revenue Leakage Radar
            </div>
          </div>
        </Reveal>

        <div className="mt-20 flex flex-col gap-4 border-t border-line pt-8 text-xs text-muted-foreground md:flex-row md:items-center md:justify-between">
          <span>© {new Date().getFullYear()} Radar Instruments. Crafted with precision.</span>
          <div className="flex gap-6">
            <Link href="/upload" className="transition-colors hover:text-foreground">
              Upload
            </Link>
            <Link href="/report" className="transition-colors hover:text-foreground">
              Report
            </Link>
            <Link href="/workspace" className="transition-colors hover:text-foreground">
              Workspace
            </Link>
          </div>
        </div>
      </div>
    </footer>
  )
}
