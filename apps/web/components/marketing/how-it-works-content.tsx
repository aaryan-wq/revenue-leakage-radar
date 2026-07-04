import Link from "next/link";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import {
  VERIFICATION_RULE_CATEGORIES,
  VERIFICATION_RULE_COUNT,
} from "@/lib/verification-rules";

export const VERIFICATION_CHECK_CATEGORIES = VERIFICATION_RULE_CATEGORIES;
export const VERIFICATION_CHECK_COUNT = VERIFICATION_RULE_COUNT;

export const AUDIT_WORKFLOW = [
  { step: "01", title: "Upload CSVs", body: "Drop billing and CRM exports from Stripe, Chargebee, HubSpot, Salesforce, or your stack. No account required." },
  { step: "02", title: "Validation", body: "We verify headers, relationships, and data quality before any analysis runs." },
  {
    step: "03",
    title: "Verification Engine",
    body: `${VERIFICATION_RULE_COUNT} deterministic checks reconcile pricing, discounts, renewals, contracts, billing cadence, and data quality. Every compatible rule runs on your data.`,
  },
  { step: "04", title: "Free Summary", body: "See estimated recoverable ARR, top categories, coverage, and confidence scores." },
  { step: "05", title: "Unlock Revenue Verification Report", body: "Purchase when ready for customer-level evidence, calculation traces, and remediation steps." },
] as const;

export const METHOD_STEPS = [
  {
    n: "01",
    title: "Reconcile",
    body: "We ingest billing and CRM exports from payment processors, ledgers, and sales systems, then align every transaction across systems.",
  },
  {
    n: "02",
    title: "Detect",
    body: "Each revenue path is examined against intended behavior. Where reality diverges, we measure the gap and annualize impact.",
  },
  {
    n: "03",
    title: "Recover",
    body: "Findings arrive ranked by recoverable dollars, supported by evidence, with precise remediation guidance.",
  },
] as const;

interface HowItWorksContentProps {
  variant?: "page" | "section";
}

export function HowItWorksContent({ variant = "page" }: HowItWorksContentProps) {
  const isPage = variant === "page";

  return (
    <div className={isPage ? "mx-auto max-w-marketing px-6 py-28 md:px-10" : "mx-auto max-w-marketing px-6 py-20 md:px-10"}>
      <Reveal>
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          How it works
        </p>
        <h2
          className={
            isPage
              ? "mt-4 font-heading text-[clamp(2rem,4.5vw,3.4rem)] leading-[1.02] tracking-tight text-balance"
              : "mt-3 max-w-2xl font-heading text-[clamp(1.9rem,4vw,3rem)] leading-[1.05] tracking-tight text-balance"
          }
        >
          From CSV export to recoverable revenue in minutes.
        </h2>
        <p className="mt-4 max-w-2xl leading-relaxed text-muted-foreground">
          No integrations. No manual spreadsheets. Upload your billing and CRM data and let the verification
          engine surface what you are leaving on the table.
        </p>
      </Reveal>

      <Stagger className="mt-16 space-y-0">
        {AUDIT_WORKFLOW.map((item) => (
          <StaggerItem key={item.step}>
            <div className="grid gap-4 border-t border-line py-8 md:grid-cols-[4rem_1fr]">
              <span className="font-heading text-sm text-primary tnum">{item.step}</span>
              <div>
                <h3 className="font-heading text-xl tracking-tight">{item.title}</h3>
                <p className="mt-2 leading-relaxed text-muted-foreground">{item.body}</p>
              </div>
            </div>
          </StaggerItem>
        ))}
      </Stagger>

      <Reveal delay={0.08} className="mt-20">
        <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          Verification engine
        </p>
        <h3 className="mt-4 max-w-2xl font-heading text-[clamp(1.6rem,3.5vw,2.4rem)] leading-[1.05] tracking-tight text-balance">
          {VERIFICATION_RULE_COUNT} deterministic checks. Zero guesswork.
        </h3>
        <p className="mt-4 max-w-2xl leading-relaxed text-muted-foreground">
          Every check is a pure function over your canonical billing data, not AI inference. Each
          finding includes evidence, estimated monthly and annual leakage, and a confidence score
          based on data coverage. Upload more exports to unlock additional checks; we never block
          the free scan when data is partial.
        </p>
        <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
          <span className="font-medium tabular-nums text-foreground">{VERIFICATION_RULE_COUNT}</span>{" "}
          rules ship in the product today, grouped across pricing, discounts, billing, credits, and
          data quality.
        </p>
      </Reveal>

      <Stagger className="mt-12 grid gap-8 md:grid-cols-2">
        {VERIFICATION_RULE_CATEGORIES.map((category) => (
          <StaggerItem key={category.label}>
            <div className="h-full rounded-xl border border-line p-6">
              <h4 className="font-heading text-lg tracking-tight">{category.label}</h4>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {category.description}
              </p>
              <ul className="mt-5 space-y-4">
                {category.checks.map((check) => (
                  <li key={check.name} className="border-t border-line pt-4 first:border-t-0 first:pt-0">
                    <p className="text-sm font-medium text-foreground">{check.name}</p>
                    <p className="mt-1 text-sm leading-relaxed text-muted-foreground">{check.detail}</p>
                  </li>
                ))}
              </ul>
            </div>
          </StaggerItem>
        ))}
      </Stagger>

      <Reveal delay={0.1} className="mt-12">
        <p className="mb-6 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
          The method
        </p>
        <div className="grid gap-10 md:grid-cols-3">
          {METHOD_STEPS.map((s) => (
            <div key={s.n}>
              <div className="mb-4 flex items-baseline gap-3 border-t border-line pt-4">
                <span className="font-heading text-sm text-primary tnum">{s.n}</span>
                <span className="font-heading text-xl tracking-tight">{s.title}</span>
              </div>
              <p className="text-pretty leading-relaxed text-muted-foreground">{s.body}</p>
            </div>
          ))}
        </div>
      </Reveal>

      {isPage && (
        <Reveal delay={0.15} className="mt-16 flex flex-wrap items-center gap-6">
          <RunFreeAuditCta size="lg" />
          <Link
            href="/security"
            className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
          >
            Review our security practices →
          </Link>
        </Reveal>
      )}
    </div>
  );
}
