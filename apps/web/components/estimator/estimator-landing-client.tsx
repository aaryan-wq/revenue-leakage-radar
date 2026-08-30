"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { glide, Reveal, Stagger, StaggerItem } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { captureEvent } from "@/lib/analytics/client";
import { AnalyticsEvents } from "@rlr/shared";
import { useTrackOnce } from "@/lib/analytics/hooks";

const TRUST_ITEMS = [
  "No billing data required",
  "No account required",
  "Transparent assumptions",
  "Deterministic modeling",
];

export function EstimatorLandingClient() {
  useTrackOnce(AnalyticsEvents.ESTIMATOR_VIEWED, { page: "landing" });

  return (
    <div className="mx-auto max-w-marketing px-6 pb-24 pt-16 md:px-10 md:pt-20">
      <Reveal className="mx-auto max-w-readable text-center">
        <p className="text-overline text-muted-foreground">Free calculator</p>
        <h1 className="text-display-hero mt-4 text-foreground">
          How much revenue could your billing be leaking?
        </h1>
        <p className="text-body mt-6 text-muted-foreground">
          A short assessment of your pricing, contracts, and billing operations. Get a modeled range in
          minutes without uploading data.
        </p>
      </Reveal>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8, ease: glide, delay: 0.15 }}
        className="mx-auto mt-12 max-w-readable"
      >
        <HairlineCard padding="lg" className="space-y-8 text-center">
          <div className="space-y-3">
            <p className="text-h4 text-foreground">Start the assessment</p>
            <p className="text-body text-muted-foreground">
              Most teams finish in about 5 minutes. No signup, no integrations.
            </p>
          </div>
          <div className="flex flex-col items-center justify-center gap-4 sm:flex-row">
            <Link href="/saas-revenue-leakage-calculator/start">
              <Button
                size="lg"
                className="min-h-[44px]"
                onClick={() => captureEvent(AnalyticsEvents.ESTIMATOR_STARTED, { source: "landing_hero" })}
              >
                Begin assessment
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/saas-revenue-leakage-calculator/methodology">
              <Button variant="ghost" size="lg" className="min-h-[44px]">
                Methodology
              </Button>
            </Link>
          </div>
        </HairlineCard>
      </motion.div>

      <Stagger className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {TRUST_ITEMS.map((item) => (
          <StaggerItem key={item}>
            <HairlineCard padding="md" className="h-full text-center">
              <p className="text-small text-foreground">{item}</p>
            </HairlineCard>
          </StaggerItem>
        ))}
      </Stagger>

      <Reveal className="mt-20 mx-auto max-w-readable text-center">
        <p className="text-body text-muted-foreground">
          Want evidence from your actual billing records? Run the free deterministic scan on the main product.
        </p>
        <Link href="/upload" className="mt-6 inline-block">
          <Button variant="secondary" className="min-h-[44px]">
            Run free billing scan
          </Button>
        </Link>
      </Reveal>
    </div>
  );
}
