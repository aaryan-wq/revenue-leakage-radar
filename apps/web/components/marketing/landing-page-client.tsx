"use client";

import { ArrLeakageHero } from "@/components/marketing/arr-leakage-hero";
import { FreeReportPreview } from "@/components/marketing/free-report-preview";
import { SecuritySummary } from "@/components/marketing/security-summary";
import { LandingPageTracker } from "@/components/analytics/marketing-page-tracker";
import { SiteFooter } from "@/components/site-footer";
import { cn } from "@/lib/utils";

const STATS = [
  { value: "8", label: "Billing and CRM platforms supported" },
  { value: "4", label: "Data coverage tiers" },
  { value: "94%", label: "Median finding confidence" },
  { value: "100%", label: "Deterministic financial math" },
];

const METHOD_STEPS = [
  {
    title: "Reconcile",
    body: "We ingest billing and CRM exports from your payment processor, ledger, and sales systems, then align every transaction across systems. No integration required.",
  },
  {
    title: "Detect",
    body: "Each revenue path is examined against its intended behavior. Where reality diverges from policy, we measure the gap and annualize the impact.",
  },
  {
    title: "Present",
    body: "Findings arrive as a board-ready report: ranked by recoverable dollars, supported by evidence, and paired with a precise remedy.",
  },
];

function MethodSection() {
  return (
    <section className="mx-auto max-w-marketing px-6 py-16 md:px-10 md:py-24">
      <h2 className="text-h1 max-w-2xl text-balance text-foreground">
        Three deliberate movements, from raw export to recovered revenue.
      </h2>

      <div className="mt-12 grid gap-10 md:mt-16 md:grid-cols-3">
        {METHOD_STEPS.map((step, index) => (
          <div key={step.title} className="border-t-2 border-primary pt-5">
            <p className="text-sm tabular-nums text-primary">0{index + 1}</p>
            <h3 className="text-h4 mt-2 text-foreground">{step.title}</h3>
            <p className="text-body mt-3 text-muted-foreground">{step.body}</p>
          </div>
        ))}
      </div>
    </section>
  );
}

export function LandingPageClient() {
  return (
    <>
      <LandingPageTracker />
      <ArrLeakageHero />

      <section className="border-y border-line bg-background">
        <div className="mx-auto grid max-w-marketing grid-cols-2 md:grid-cols-4">
          {STATS.map((stat, index) => (
            <div
              key={stat.label}
              className={cn(
                "px-6 py-8 md:px-10 md:py-10",
                index % 2 === 1 && "border-l border-line",
                index >= 2 && "border-t border-line md:border-t-0",
                index > 0 && "md:border-l md:border-line",
              )}
            >
              <p className="text-h2 tabular-nums text-primary">{stat.value}</p>
              <p className="text-small mt-2 max-w-[16rem] text-muted-foreground">{stat.label}</p>
            </div>
          ))}
        </div>
      </section>

      <MethodSection />
      <SecuritySummary />
      <FreeReportPreview />
      <SiteFooter />
    </>
  );
}
