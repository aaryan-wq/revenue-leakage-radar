"use client";

import Link from "next/link";

import { Logo } from "@/components/brand/logo";
import { Reveal } from "@/components/motion";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { cn } from "@/lib/utils";

type SiteFooterProps = {
  variant?: "default" | "minimal";
  className?: string;
};

export function SiteFooter({ variant = "default", className }: SiteFooterProps) {
  if (variant === "minimal") {
    return (
      <footer className={cn("border-t border-line", className)}>
        <div className="mx-auto flex max-w-marketing flex-col gap-4 px-6 py-8 text-xs text-muted-foreground md:flex-row md:items-center md:justify-between md:px-10">
          <span>© {new Date().getFullYear()} Paevo.</span>
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
            <Link href="/terms" className="transition-colors hover:text-foreground">
              Terms
            </Link>
            <Link href="/privacy" className="transition-colors hover:text-foreground">
              Privacy
            </Link>
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className={cn("border-t border-line", className)}>
      <div className="mx-auto max-w-marketing px-6 py-16 md:px-10 md:py-24">
        <Reveal>
          <div className="flex flex-col items-start justify-between gap-10 md:flex-row md:items-end md:gap-12">
            <div className="max-w-xl">
              <h2 className="font-heading text-[clamp(1.75rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance">
                How much revenue are your billing and CRM systems leaving behind?
              </h2>
              <p className="mt-5 leading-relaxed text-muted-foreground md:mt-6">
                Upload your exports. Get a free audit in minutes. Unlock the Revenue Verification
                Report when the numbers justify it.
              </p>
              <div className="mt-8 w-full sm:w-auto">
                <RunFreeAuditCta size="md" className="w-full sm:w-auto" />
              </div>
            </div>
            <Logo variant="full" className="h-10 sm:h-12 md:h-14" />
          </div>
        </Reveal>

        <div className="mt-14 flex flex-col gap-5 border-t border-line pt-8 text-xs text-muted-foreground md:mt-20 md:flex-row md:items-center md:justify-between">
          <span>© {new Date().getFullYear()} Paevo.</span>
          <div className="grid grid-cols-2 gap-x-4 gap-y-3 sm:flex sm:flex-wrap sm:gap-x-6 sm:gap-y-2">
            <Link href="/how-it-works" className="transition-colors hover:text-foreground">
              How It Works
            </Link>
            <Link href="/demo" className="transition-colors hover:text-foreground">
              Demo
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
            <Link href="/feedback" className="transition-colors hover:text-foreground">
              Feedback
            </Link>
            <Link href="/terms" className="transition-colors hover:text-foreground">
              Terms
            </Link>
            <Link href="/privacy" className="transition-colors hover:text-foreground">
              Privacy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
