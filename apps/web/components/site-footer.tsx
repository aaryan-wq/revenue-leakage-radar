"use client";

import Link from "next/link";

import { Reveal } from "@/components/motion";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";

export function SiteFooter() {
  return (
    <footer className="border-t border-line">
      <div className="mx-auto max-w-marketing px-6 py-24 md:px-10">
        <Reveal>
          <div className="flex flex-col items-start justify-between gap-12 md:flex-row md:items-end">
            <div className="max-w-xl">
              <h2 className="font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
                How much revenue is your billing system leaving behind?
              </h2>
              <p className="mt-6 leading-relaxed text-muted-foreground">
                Upload your exports. Get a free summary in minutes. Unlock the full report when the
                numbers justify it.
              </p>
              <div className="mt-8">
                <RunFreeAuditCta size="md" />
              </div>
            </div>
            <div className="flex items-center gap-2 text-sm text-muted-foreground">
              <span className="h-2 w-2 rounded-full bg-primary" />
              Revenue Leakage Radar
            </div>
          </div>
        </Reveal>

        <div className="mt-20 flex flex-col gap-4 border-t border-line pt-8 text-xs text-muted-foreground md:flex-row md:items-center md:justify-between">
          <span>© {new Date().getFullYear()} Radar Instruments.</span>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            <Link href="/how-it-works" className="transition-colors hover:text-foreground">
              How It Works
            </Link>
            <Link href="/pricing" className="transition-colors hover:text-foreground">
              Pricing
            </Link>
            <Link href="/security" className="transition-colors hover:text-foreground">
              Security
            </Link>
            <Link href="/faq" className="transition-colors hover:text-foreground">
              FAQ
            </Link>
            <Link href="/contact" className="transition-colors hover:text-foreground">
              Contact
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
