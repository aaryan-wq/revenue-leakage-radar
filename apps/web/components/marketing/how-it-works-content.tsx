import Link from "next/link";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";

export const AUDIT_WORKFLOW = [
  { step: "01", title: "Upload CSVs", body: "Drop billing exports from Stripe, Chargebee, or your billing system. No account required." },
  { step: "02", title: "Validation", body: "We verify headers, relationships, and data quality before any analysis runs." },
  { step: "03", title: "Verification Engine", body: "Deterministic rules reconcile pricing, discounts, renewals, and catalog mismatches." },
  { step: "04", title: "Free Summary", body: "See estimated recoverable ARR, top categories, coverage, and confidence scores." },
  { step: "05", title: "Unlock Detailed Report", body: "Purchase when ready for customer names, invoice evidence, and remediation steps." },
] as const;

export const METHOD_STEPS = [
  {
    n: "01",
    title: "Reconcile",
    body: "We ingest exports from billing, payment processors, and your ledger — then align every transaction across systems.",
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
          No integrations. No manual spreadsheets. Upload your billing data and let the verification
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
