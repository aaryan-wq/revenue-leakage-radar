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

const HEADLINE_LINES = ["Your billing exports", "hold recoverable", "revenue"];

export function ArrLeakageHero() {
  const [position, setPosition] = useState(() => sliderPositionFromArr(LANDING_ARR_DEFAULT));

  const arr = useMemo(() => arrFromSliderPosition(position), [position]);
  const estimate = useMemo(() => estimateLandingLeakage(arr), [arr]);

  return (
    <section className="relative mx-auto max-w-marketing px-6 pt-12 pb-12 md:px-10 md:pt-28 md:pb-20">
      <div className="grid grid-cols-1 items-center gap-10 lg:grid-cols-2 lg:gap-16">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.9, ease: glide, delay: 0.1 }}
          className="order-2 w-full lg:order-1"
        >
          <HairlineCard
            padding="none"
            className="relative overflow-hidden border-primary/15 p-6 md:p-10"
          >
            <div
              className="pointer-events-none absolute inset-0"
              style={{
                background:
                  "radial-gradient(90% 70% at 50% 0%, color-mix(in oklch, var(--primary) 7%, transparent), transparent 70%)",
              }}
            />

            <div className="relative space-y-6 md:space-y-8">
              <div className="rounded-xl border border-line bg-secondary/35 px-5 py-6 text-center md:px-8 md:py-8">
                <p className="text-overline text-muted-foreground">Industry leakage benchmark</p>
                <motion.p
                  key={estimate.headlineUsd}
                  initial={{ opacity: 0.65, y: 4 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.25, ease: glide }}
                  className="text-metric-xl mt-3 font-heading text-[clamp(1.75rem,8vw,3rem)] tracking-tight tabular-nums text-foreground md:mt-4"
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

              <div className="space-y-4 rounded-xl border border-dashed border-line bg-card/50 px-5 py-5 md:space-y-5 md:px-6 md:py-6">
                <div className="flex items-end justify-between gap-4">
                  <label htmlFor="landing-arr-slider" className="text-h4 text-foreground">
                    Your ARR
                  </label>
                  <p className="font-heading text-xl tracking-tight tabular-nums text-foreground md:text-2xl">
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

              <p className="text-left text-caption text-muted-foreground">
                Illustrative benchmark only. Upload billing exports below for deterministic findings
                from your records.
              </p>
            </div>
          </HairlineCard>
        </motion.div>

        <Reveal className="order-1 text-center lg:order-2 lg:text-left">
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide }}
            className="text-overline text-muted-foreground"
          >
            Revenue Leakage Radar
          </motion.p>
          <h1 className="mt-3 font-heading text-[clamp(2.1rem,9vw,4rem)] leading-[0.96] tracking-tight text-balance text-foreground md:mt-4 md:text-[clamp(2.4rem,5vw,4rem)]">
            {HEADLINE_LINES.map((line, i) => (
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
            className="mx-auto mt-5 max-w-readable text-body leading-relaxed text-muted-foreground md:mt-6 lg:mx-0 lg:max-w-none"
          >
            Upload billing and CRM CSV exports. Our engine reconciles every row and surfaces missed
            revenue, duplicate charges, and pricing drift in minutes.
          </motion.p>
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide, delay: 0.65 }}
            className="mt-8 flex flex-col items-center gap-2 sm:flex-row sm:flex-wrap sm:justify-center sm:gap-x-6 sm:gap-y-2 lg:mt-10 lg:justify-start"
          >
            {["Deterministic rules", "Evidence-backed findings", "No integrations"].map((item) => (
              <span key={item} className="flex items-center gap-2 text-small text-muted-foreground">
                <span className="h-1 w-1 rounded-full bg-primary/50" />
                {item}
              </span>
            ))}
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.9, ease: glide, delay: 0.8 }}
            className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-center lg:mt-10 lg:justify-start"
          >
            <Link href="/upload" className="w-full sm:w-auto">
              <Button
                size="lg"
                className="min-h-[44px] w-full sm:w-auto"
                onClick={() =>
                  captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED, { source: "landing_hero" })
                }
              >
                Run free billing scan
                <ArrowRight className="ml-2 h-4 w-4" />
              </Button>
            </Link>
            <Link href="/saas-revenue-leakage-calculator/start" className="w-full sm:w-auto">
              <Button
                variant="ghost"
                size="lg"
                className="min-h-[44px] w-full sm:w-auto"
                onClick={() =>
                  captureEvent(AnalyticsEvents.ESTIMATOR_STARTED, { source: "landing_slider" })
                }
              >
                Quick assessment instead
              </Button>
            </Link>
          </motion.div>
        </Reveal>
      </div>
    </section>
  );
}
