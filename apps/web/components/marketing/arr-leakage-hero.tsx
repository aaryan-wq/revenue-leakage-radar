"use client";

import Link from "next/link";
import { useMemo, useState } from "react";

import { AssessmentStartPicker } from "@/components/estimator/estimator-landing-client";
import { Button } from "@/components/ui/button";
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
    <section className="bg-field">
      <div className="mx-auto max-w-marketing px-6 py-16 md:px-10 md:py-24">
      <div className="grid items-start gap-12 lg:grid-cols-2 lg:gap-20">
        <div>
          <h1 className="text-display max-w-xl text-balance text-foreground">
            Your billing exports hold recoverable revenue.
          </h1>
          <p className="text-body mt-5 max-w-md text-muted-foreground">
            Upload billing and CRM CSV exports. Our engine reconciles every row and surfaces missed
            revenue, duplicate charges, and pricing drift in minutes.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:items-center">
            <Link href="/upload" className="w-full sm:w-auto">
              <Button
                size="lg"
                className="w-full sm:w-auto"
                onClick={() =>
                  captureEvent(AnalyticsEvents.FREE_AUDIT_CTA_CLICKED, { source: "landing_hero" })
                }
              >
                Run free billing scan
              </Button>
            </Link>
            <Link href="/demo" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto"
                onClick={() =>
                  captureEvent(AnalyticsEvents.DEMO_CTA_CLICKED, {
                    source: "landing_hero",
                    destination: "demo_report",
                  })
                }
              >
                View sample report
              </Button>
            </Link>
          </div>
        </div>

        <div className="lg:pt-2">
          <p className="text-sm text-muted-foreground">Typical leakage at your ARR</p>
          <p className="text-metric-xl mt-3 text-primary">
            {formatCurrency(estimate.headlineUsd)}
            <span className="text-h4 font-normal text-muted-foreground"> /year</span>
          </p>
          <p className="text-small mt-3 tabular-nums text-muted-foreground">
            {formatCurrency(estimate.lowUsd)} to {formatCurrency(estimate.highUsd)}. Industry average
            is 4.2% of ARR.
          </p>

          <div className="mt-8">
            <div className="flex items-baseline justify-between gap-4">
              <label htmlFor="landing-arr-slider" className="text-sm text-foreground">
                Your ARR
              </label>
              <p className="text-sm tabular-nums text-foreground">{formatArrLabel(arr)}</p>
            </div>
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
              className="landing-arr-slider mt-4 h-1 w-full cursor-pointer appearance-none rounded-full bg-background"
              aria-valuemin={LANDING_ARR_MIN}
              aria-valuemax={LANDING_ARR_MAX}
              aria-valuenow={arr}
              aria-valuetext={formatArrLabel(arr)}
            />
            <div className="mt-2 flex justify-between text-xs tabular-nums text-muted-foreground">
              <span>{formatArrLabel(1_000_000)}</span>
              <span>{formatArrLabel(100_000_000)}</span>
            </div>
          </div>

          <p className="text-caption mt-6 text-muted-foreground">
            Illustrative benchmark only. Upload billing exports for deterministic findings from your
            records.
          </p>
        </div>
      </div>

      <div className="mt-14 border-t border-line pt-10 md:mt-16 md:pt-12">
        <AssessmentStartPicker source="home_hero" plain layout="columns" />
      </div>
      </div>
    </section>
  );
}
