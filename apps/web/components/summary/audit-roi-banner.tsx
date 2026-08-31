"use client";

import { TrendingUp } from "lucide-react";

import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";
import {
  AUDIT_ROI_DISCLAIMER,
  VALUATION_FRAMING,
  buildBelowBreakEvenHeadline,
  buildBelowBreakEvenSubhead,
  buildPositiveRoiHeadline,
  buildPositiveRoiStats,
  buildPositiveRoiSubhead,
} from "@/lib/audit-roi-content";
import { computeAuditRoiFromAmount } from "@rlr/shared";

interface AuditRoiBannerProps {
  recoverableArr: string;
}

export function AuditRoiBanner({ recoverableArr }: AuditRoiBannerProps) {
  const metrics = computeAuditRoiFromAmount(recoverableArr);
  if (!metrics) {
    return null;
  }

  if (!metrics.isPositiveRoi) {
    return (
      <section className="border-t border-line pt-12 pb-12">
        <Reveal>
          <HairlineCard padding="lg" subtle className="border-line">
            <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
              Audit ROI
            </p>
            <h2 className="mt-4 font-heading text-2xl tracking-tight text-foreground md:text-3xl">
              {buildBelowBreakEvenHeadline()}
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              {buildBelowBreakEvenSubhead()}
            </p>
            <p className="mt-4 text-xs leading-relaxed text-muted-foreground">{AUDIT_ROI_DISCLAIMER}</p>
          </HairlineCard>
        </Reveal>
      </section>
    );
  }

  const stats = buildPositiveRoiStats(metrics);

  return (
    <section className="border-t border-line pt-12 pb-12">
      <Reveal>
        <HairlineCard padding="lg" elevated className="border-line">
          <div className="flex items-start gap-4">
            <div className="hidden rounded-full border border-line bg-secondary/40 p-3 sm:block">
              <TrendingUp className="h-5 w-5 text-foreground" strokeWidth={1.75} aria-hidden />
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
                Audit ROI
              </p>
              <h2 className="mt-4 font-heading text-[clamp(1.75rem,4vw,2.5rem)] leading-tight tracking-tight text-foreground">
                {buildPositiveRoiHeadline(metrics)}
              </h2>
              <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
                {buildPositiveRoiSubhead(recoverableArr)}
              </p>

              <dl className="mt-8 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2">
                {stats.map((stat) => (
                  <div key={stat.label} className="bg-card px-5 py-5">
                    <dt className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                      {stat.label}
                    </dt>
                    <dd className="mt-2 font-heading text-2xl tracking-tight tnum text-foreground">
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
              <p className="mt-3 text-xs leading-relaxed text-muted-foreground">{AUDIT_ROI_DISCLAIMER}</p>
            </div>
          </div>
        </HairlineCard>
      </Reveal>
    </section>
  );
}
