"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import { ArrowRight, ShieldCheck } from "lucide-react";

import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { captureEvent } from "@/lib/analytics/client";
import { AnalyticsEvents } from "@rlr/shared";
import { useTrackOnce } from "@/lib/analytics/hooks";

const TRUST_ITEMS = [
  "No billing data required",
  "Deterministic financial modeling",
  "Transparent assumptions",
  "No mystery AI score",
];

export function EstimatorLandingClient() {
  useTrackOnce(AnalyticsEvents.ESTIMATOR_VIEWED, { page: "landing" });

  return (
    <div className="mx-auto max-w-marketing px-6 pb-24 pt-16 md:px-10 md:pt-24">
      <Reveal className="mx-auto max-w-readable text-center">
        <p className="text-overline text-muted-foreground">Free microtool</p>
        <h1 className="text-display-hero mt-4 text-foreground">
          How much recurring revenue could your SaaS be leaking?
        </h1>
        <p className="text-body mt-6 text-muted-foreground">
          Answer a few questions about your pricing, contracts, discounts and billing operations.
          Get a modeled leakage range in minutes, without uploading billing data.
        </p>
        <div className="mt-10 flex flex-col items-center justify-center gap-4 sm:flex-row">
          <Link href="/saas-revenue-leakage-calculator/start">
            <Button
              size="lg"
              className="min-h-[44px]"
              onClick={() => captureEvent(AnalyticsEvents.ESTIMATOR_STARTED, { source: "landing_hero" })}
            >
              Estimate My Revenue Leakage
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </Link>
          <Link href="/saas-revenue-leakage-calculator/methodology">
            <Button variant="ghost" size="lg" className="min-h-[44px]">
              How it works
            </Button>
          </Link>
        </div>
        <p className="text-caption mt-4 text-muted-foreground">
          No billing data. No integrations. No signup required.
        </p>
      </Reveal>

      <div className="mt-16 grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {TRUST_ITEMS.map((item) => (
          <HairlineCard key={item} padding="md" className="text-center">
            <ShieldCheck className="mx-auto mb-3 h-5 w-5 text-muted-foreground" />
            <p className="text-small text-foreground">{item}</p>
          </HairlineCard>
        ))}
      </div>

      <motion.div
        initial={{ opacity: 0, y: 12 }}
        whileInView={{ opacity: 1, y: 0 }}
        viewport={{ once: true }}
        className="mt-20 mx-auto max-w-readable text-center"
      >
        <p className="text-body text-muted-foreground">
          This is a free calculator on our marketing site. For evidence-backed findings from your billing
          records, use the main product scan.
        </p>
        <Link href="/upload" className="mt-6 inline-block">
          <Button variant="secondary" className="min-h-[44px]">
            Run Free Revenue Scan
          </Button>
        </Link>
      </motion.div>
    </div>
  );
}
