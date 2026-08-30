"use client";

import Link from "next/link";
import { ArrowRight, BarChart3, Calculator, ShieldCheck } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { clearAssessmentSession } from "@/lib/estimator/api";

const STEPS = [
  {
    icon: Calculator,
    title: "Your inputs",
    body: "You answer questions about pricing models, contracts, discounts, billing systems, and controls. No CSV uploads or integrations.",
  },
  {
    icon: BarChart3,
    title: "Deterministic model",
    body: "Answers map to 18 leakage hypotheses, segment your revenue profile, adjust for overlap, and run a fixed-seed Monte Carlo simulation.",
  },
  {
    icon: ShieldCheck,
    title: "Modeled range",
    body: "You receive a low-to-high ARR range with drivers and assumptions. It is directional guidance, not an audited billing finding.",
  },
] as const;

const LIMITS = [
  "Does not inspect customer records or invoices.",
  "Uses structural priors at launch (Stage 0), not calibrated audit outcomes yet.",
  "Ranges overlap across drivers and should not be summed independently.",
  "AI narrative, when shown, summarizes the model. It never sets the numbers.",
];

export function EstimatorMethodologyClient() {
  const handleRestart = () => {
    clearAssessmentSession();
    window.location.href = "/saas-revenue-leakage-calculator/start";
  };

  return (
    <div className="mx-auto max-w-marketing px-6 pb-20 pt-16 md:px-10 md:pt-20">
      <Reveal className="mx-auto max-w-readable text-center">
        <p className="text-overline text-muted-foreground">Calculator methodology</p>
        <h1 className="text-h1 mt-4 text-foreground">How the estimate is built</h1>
        <p className="text-body mt-6 text-muted-foreground">
          A transparent, deterministic model for directional leakage exposure. Built for finance
          leaders who want a starting point before uploading billing data.
        </p>
      </Reveal>

      <Stagger className="mt-16 grid gap-6 md:grid-cols-3">
        {STEPS.map((step) => (
          <StaggerItem key={step.title}>
            <HairlineCard padding="lg" className="h-full space-y-4">
              <step.icon className="h-5 w-5 text-muted-foreground" strokeWidth={1.75} />
              <h2 className="text-h4 text-foreground">{step.title}</h2>
              <p className="text-body text-muted-foreground">{step.body}</p>
            </HairlineCard>
          </StaggerItem>
        ))}
      </Stagger>

      <div className="mt-16 grid gap-6 md:grid-cols-2">
        <Reveal>
          <HairlineCard padding="lg" className="space-y-5">
            <div>
              <p className="text-overline text-muted-foreground">Headline range</p>
              <h2 className="text-h4 mt-2">What the numbers mean</h2>
            </div>
            <ul className="space-y-3 text-body text-muted-foreground">
              <li className="flex gap-3">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                <span>The displayed range uses the 25th to 75th percentile of simulated outcomes.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                <span>Scenario toggles shift priors conservative, expected, or upside without changing your answers.</span>
              </li>
              <li className="flex gap-3">
                <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                <span>Billing complexity is scored separately and never multiplied directly against ARR.</span>
              </li>
            </ul>
          </HairlineCard>
        </Reveal>

        <Reveal>
          <HairlineCard padding="lg" className="space-y-5">
            <div>
              <p className="text-overline text-muted-foreground">Limits</p>
              <h2 className="text-h4 mt-2">What this is not</h2>
            </div>
            <ul className="space-y-3 text-body text-muted-foreground">
              {LIMITS.map((line) => (
                <li key={line} className="flex gap-3">
                  <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-primary/70" />
                  <span>{line}</span>
                </li>
              ))}
            </ul>
          </HairlineCard>
        </Reveal>
      </div>

      <Reveal className="mt-16">
        <HairlineCard padding="lg" className="mx-auto max-w-readable space-y-6 text-center">
          <div className="space-y-3">
            <h2 className="text-h3 text-foreground">Ready for evidence?</h2>
            <p className="text-body text-muted-foreground">
              Use the calculator for a quick directional read. Upload billing exports when you want
              deterministic findings backed by records.
            </p>
          </div>
          <div className="flex flex-col items-center justify-center gap-3 sm:flex-row">
            <Link href="/saas-revenue-leakage-calculator/start">
              <Button className="min-h-[44px]">Start assessment</Button>
            </Link>
            <Button variant="secondary" onClick={handleRestart} className="min-h-[44px]">
              Retake assessment
            </Button>
            <Link href="/upload">
              <Button variant="ghost" className="min-h-[44px]">
                Run billing scan
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
          </div>
        </HairlineCard>
      </Reveal>
    </div>
  );
}
