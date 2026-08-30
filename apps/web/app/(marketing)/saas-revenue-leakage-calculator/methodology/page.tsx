import type { Metadata } from "next";
import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";

export const metadata: Metadata = {
  title: "Revenue Leakage Estimator Methodology | Paevo",
  description: "How Paevo models SaaS revenue leakage exposure without billing data.",
};

export default function EstimatorMethodologyPage() {
  return (
    <>
      <div className="mx-auto max-w-readable space-y-8 px-6 py-16 md:px-10">
        <HairlineCard padding="lg" className="space-y-6">
          <h1 className="text-h1">How the SaaS Revenue Leakage Estimator works</h1>
          <p className="text-body text-muted-foreground">
            This free microtool models potential exposure from self-reported billing characteristics.
            It is not a billing finding and does not inspect customer records.
          </p>
          <div className="space-y-4 text-body text-muted-foreground">
            <p>
              Answers feed a deterministic pipeline: segmentation, H1 to H18 hypothesis propensity scores,
              exposure decomposition, correlation overlap adjustment, and Monte Carlo simulation with a
              fixed random seed for reproducibility.
            </p>
            <p>
              Headline ranges use the 25th to 75th percentile of simulated outcomes. Complexity is scored
              separately and never multiplied directly against ARR.
            </p>
            <p>
              Model maturity at launch: Stage 0 structural priors. Calibration against audited outcomes
              will be documented as sample sizes allow.
            </p>
          </div>
          <Link href="/saas-revenue-leakage-calculator/start">
            <Button className="min-h-[44px]">Start free assessment</Button>
          </Link>
          <Link href="/upload" className="ml-4 inline-block">
            <Button variant="secondary" className="min-h-[44px]">
              Run free billing scan
            </Button>
          </Link>
        </HairlineCard>
      </div>
      <SiteFooter />
    </>
  );
}
