"use client";

import Link from "next/link";
import { Sparkles } from "lucide-react";

import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";

export function DemoBanner() {
  return (
    <div className="border-b border-line bg-secondary/40 backdrop-blur-lg">
      <div className="mx-auto flex max-w-report flex-col gap-4 px-6 py-4 md:flex-row md:items-center md:justify-between md:px-10">
        <div className="flex items-start gap-3">
          <Sparkles className="mt-0.5 h-4 w-4 shrink-0 text-primary" strokeWidth={1.75} />
          <p className="text-sm leading-relaxed text-muted-foreground">
            <span className="font-medium text-foreground">Sample report.</span> You are viewing a
            verification report for AcmeCRM. All customer and invoice data is fictional.
          </p>
        </div>
        <div className="flex shrink-0 items-center gap-3">
          <Link
            href="/"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Back to home
          </Link>
          <RunFreeAuditCta
            size="sm"
            showArrow={false}
            analyticsSource="demo_banner"
            className="[&_span]:shadow-none"
          />
        </div>
      </div>
    </div>
  );
}
