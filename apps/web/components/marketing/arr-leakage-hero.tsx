"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { motion } from "framer-motion";
import { ArrowRight } from "lucide-react";

import { glide, Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/glass-card";
import { captureEvent } from "@/lib/analytics/client";
import {
  LANDING_ARR_DEFAULT,
  LANDING_ARR_MAX,
  LANDING_ARR_MIN,
  arrFromSliderPosition,
  estimateLandingLeakage,
  formatArrLabel,
  sliderPositionFromArr,
} from "@/lib/landing-leakage-estimate";
import { AnalyticsEvents, formatCurrency } from "@rlr/shared";

export function ArrLeakageHero() {
  const [position, setPosition] = useState(() => sliderPositionFromArr(LANDING_ARR_DEFAULT));

  const arr = useMemo(() => arrFromSliderPosition(position), [position]);
  const estimate = useMemo(() => estimateLandingLeakage(arr), [arr]);

  return (
    <section className="relative mx-auto max-w-marketing px-6 pt-20 pb-16 md:px-10 md:pt-28 md:pb-20">
      <div className="grid grid-cols-1 items-center gap-12 lg:grid-cols-2 lg:gap-16">
        <Reveal className="text-center lg:text-left">
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide }}
            className="text-overline text-muted-foreground"
          >
            Free revenue leakage radar
          </motion.p>
          <h1 className="mt-4 font-heading text-[clamp(2.4rem,5vw,4rem)] leading-[0.96] tracking-tight text-balance text-foreground">
            {["How much revenue", "could your billing", "be leaking?"].map((line, i) => (
              <span key={line} className="block overflow-hidden">
                <motion.span
                  className="block"
                  initial={{ y: "110%" }}
                  animate={{ y: 0 }}
                  transition={{ duration: 1.1, ease: glide, delay: 0.08 + i * 0.12 }}
                >
                  {i === 1 ? <span className="italic text-primary">{line}</span> : line}
                </motion.span>
              </span>
            ))}
          </h1>
          <motion.p
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 1, ease: glide, delay: 0.5 }}
            className="mt-6 max-w-readable text-body leading-relaxed text-muted-foreground lg:max-w-none"
          >
            Set your ARR for a quick modeled range, or upload billing CSVs below for deterministic
            findings and evidence.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide, delay: 0.65 }}
            className="mt-10 hidden flex-wrap gap-x-6 gap-y-2 lg:flex"
          >
            {["No CSV required", "About 5 minutes", "Benchmark-based range"].map((item) => (
              <span key={item} className="flex items-center gap-2 text-small text-muted-foreground">
                <span className="h-1 w-1 rounded-full bg-primary/50" />
                {item}
              </span>
            ))}
          </motion.div>
        </Reveal>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: glide, delay: 0.15 }}
          className="w-full"
        >
        <HairlineCard padding="lg" className="relative overflow-hidden border-primary/15">
          <div
            className="pointer-events-none absolute inset-0"
            style={{
              background:
                "radial-gradient(90% 70% at 50% 0%, color-mix(in oklch, var(--primary) 7%, transparent), transparent 70%)",
            }}
          />

          <div className="relative space-y-8">
            <div className="rounded-xl border border-line bg-secondary/35 px-6 py-8 text-center md:px-8">
              <p className="text-overline text-muted-foreground">Modeled recoverable range</p>
              <motion.p
                key={estimate.headlineUsd}
                initial={{ opacity: 0.65, y: 4 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25, ease: glide }}
                className="text-metric-xl mt-4 tabular-nums text-foreground"
              >
                {formatCurrency(estimate.headlineUsd)}
                <span className="text-h4 text-muted-foreground"> /year</span>
              </motion.p>
              <p className="mt-3 text-body tabular-nums text-muted-foreground">
                {formatCurrency(estimate.lowUsd)} to {formatCurrency(estimate.highUsd)} typical
              </p>
              <p className="mt-1 text-caption text-muted-foreground">
                Industry average: 4.2% of ARR
              </p>
            </div>

            <div className="space-y-5 rounded-xl border border-dashed border-line bg-card/50 px-6 py-6">
              <div className="flex items-end justify-between gap-4">
                <label htmlFor="landing-arr-slider" className="text-h4 text-foreground">
                  Your ARR
                </label>
                <p className="font-heading text-2xl tracking-tight tabular-nums text-foreground">
                  {formatArrLabel(arr)}
                </p>
              </div>
              <p className="text-small tabular-nums text-muted-foreground">
                3.0% to 5.0% of ARR in typical SaaS billing environments
              </p>

              <div className="relative pt-2">
                <input
                  id="landing-arr-slider"
                  type="range"
                  min={0}
                  max={1000}
                  step={1}
                  value={Math.round(position * 1000)}
                  onChange={(event) => {
                    setPosition(Number(event.target.value) / 1000);
                  }}
                  className="landing-arr-slider h-2 w-full cursor-pointer appearance-none rounded-full bg-secondary"
                  aria-valuemin={LANDING_ARR_MIN}
                  aria-valuemax={LANDING_ARR_MAX}
                  aria-valuenow={arr}
                  aria-valuetext={formatArrLabel(arr)}
                />
                <div className="mt-3 flex justify-between text-[0.72rem] tabular-nums text-muted-foreground">
                  <span>{formatArrLabel(1_000_000)}</span>
                  <span>{formatArrLabel(100_000_000)}</span>
                </div>
              </div>
            </div>

            <div className="flex flex-col gap-3 pt-2 sm:flex-row sm:items-center sm:justify-start">
              <Link href="/saas-revenue-leakage-calculator/start">
                <Button
                  size="lg"
                  className="min-h-[44px] w-full sm:w-auto"
                  onClick={() =>
                    captureEvent(AnalyticsEvents.ESTIMATOR_STARTED, { source: "landing_slider" })
                  }
                >
                  Refine with full assessment
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              <Link href="/saas-revenue-leakage-calculator/methodology">
                <Button variant="ghost" size="lg" className="min-h-[44px] w-full sm:w-auto">
                  How we model this
                </Button>
              </Link>
            </div>

            <p className="text-left text-caption text-muted-foreground">
              Illustrative industry benchmark only (3% to 5% of ARR, 4.2% average). A free billing scan
              verifies recoverable dollars from your actual records.
            </p>
          </div>
        </HairlineCard>
        </motion.div>
      </div>
    </section>
  );
}
