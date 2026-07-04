import Link from "next/link";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { PRICING_PREVIEW_TIERS } from "@/lib/pricing-content";

export function PricingPreview() {
  return (
    <section className="mx-auto max-w-marketing px-6 py-20 md:px-10">
      <Reveal>
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Pricing
        </p>
        <h2 className="mt-3 max-w-xl font-heading text-[clamp(1.6rem,3.5vw,2.4rem)] leading-[1.05] tracking-tight">
          Start free. Pay when the evidence justifies it.
        </h2>
        <p className="mt-4 max-w-2xl text-muted-foreground">
          Start with a free topline leakage scan. Unlock a full Revenue Verification Report when
          you need evidence-backed findings and remediation guidance.
        </p>
      </Reveal>

      <Stagger className="mt-12 grid gap-4 md:grid-cols-3">
        {PRICING_PREVIEW_TIERS.map((tier) => (
          <StaggerItem key={tier.name}>
            <div className="h-full rounded-xl border border-line bg-card p-6">
              <p className="text-sm text-muted-foreground">{tier.name}</p>
              <p className="mt-2 font-heading text-2xl tracking-tight tnum">{tier.price}</p>
              <p className="mt-1 text-xs text-muted-foreground">{tier.note}</p>
              <p className="mt-4 text-sm leading-relaxed text-foreground/80">{tier.highlight}</p>
            </div>
          </StaggerItem>
        ))}
      </Stagger>

      <Reveal delay={0.1} className="mt-10 flex flex-wrap items-center gap-6">
        <Link
          href="/pricing"
          className="rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem] transition-colors hover:bg-foreground hover:text-background"
        >
          View full pricing →
        </Link>
        <RunFreeAuditCta size="sm" />
      </Reveal>
    </section>
  );
}
