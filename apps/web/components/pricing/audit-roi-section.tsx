"use client";

import { TrendingUp } from "lucide-react";

import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";
import {
  PRICING_ROI_DISCLAIMER,
  VALUATION_FRAMING,
  buildPricingRoiHeadline,
  buildPricingRoiStats,
  buildPricingRoiSubhead,
} from "@/lib/audit-roi-content";
import { GENERIC_ROI_EXAMPLE_ARR_USD, computeAuditRoi } from "@rlr/shared";

export function AuditRoiSection() {
  const metrics = computeAuditRoi(GENERIC_ROI_EXAMPLE_ARR_USD);

  if (!metrics || !metrics.isPositiveRoi) {
    return null;
  }

  const stats = buildPricingRoiStats(metrics);

  return (
    <Reveal delay={0.1}>
      <HairlineCard padding="lg" elevated className="border-line">
        <div className="flex items-start gap-4">
          <div className="hidden rounded-full border border-line bg-field p-3 sm:block">
            <TrendingUp className="h-5 w-5 text-primary" strokeWidth={1.75} aria-hidden />
          </div>
          <div className="min-w-0 flex-1">
            <h2 className="text-h2 text-balance text-foreground">
              {buildPricingRoiHeadline(metrics)}
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              {buildPricingRoiSubhead()}
            </p>

            <dl className="mt-8 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
              {stats.map((stat) => (
                <div key={stat.label} className="bg-card px-5 py-5">
                  <dt className="text-sm text-muted-foreground">
                    {stat.label}
                  </dt>
                  <dd className="mt-2 font-heading text-xl tracking-tight text-primary tnum lg:text-2xl">
                    {stat.value}
                  </dd>
                  {stat.detail ? (
                    <dd className="mt-1 text-xs leading-relaxed text-muted-foreground">
                      {stat.detail}
                    </dd>
                  ) : null}
                </div>
              ))}
            </dl>

            <p className="mt-6 text-sm leading-relaxed text-muted-foreground">{VALUATION_FRAMING}</p>
            <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{PRICING_ROI_DISCLAIMER}</p>
          </div>
        </div>
      </HairlineCard>
    </Reveal>
  );
}
