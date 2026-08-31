"use client";

import { TrendingUp } from "lucide-react";

import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";
import {
  AUDIT_ROI_DISCLAIMER,
  VALUATION_FRAMING,
  buildGenericRoiStats,
  buildPositiveRoiHeadline,
  buildPositiveRoiSubhead,
} from "@/lib/audit-roi-content";
import {
  GENERIC_ROI_EXAMPLE_ARR_USD,
  VERIFICATION_REPORT_BASE_FEE_USD,
  computeAuditRoi,
  computeAuditRoiFromAmount,
  formatCurrency,
} from "@rlr/shared";

interface AuditRoiSectionProps {
  recoverableArr?: string | null;
}

export function AuditRoiSection({ recoverableArr }: AuditRoiSectionProps) {
  const personalized = recoverableArr != null && recoverableArr !== "";
  const metrics = personalized
    ? computeAuditRoiFromAmount(recoverableArr)
    : computeAuditRoi(GENERIC_ROI_EXAMPLE_ARR_USD);

  if (!metrics || !metrics.isPositiveRoi) {
    return null;
  }

  const stats = buildGenericRoiStats(metrics);
  const exampleAmount = personalized
    ? formatCurrency(recoverableArr)
    : formatCurrency(GENERIC_ROI_EXAMPLE_ARR_USD);

  return (
    <Reveal delay={0.1}>
      <HairlineCard padding="lg" elevated className="border-line">
        <div className="flex items-start gap-4">
          <div className="hidden rounded-full border border-line bg-secondary/40 p-3 sm:block">
            <TrendingUp className="h-5 w-5 text-foreground" strokeWidth={1.75} aria-hidden />
          </div>
          <div className="min-w-0 flex-1">
            <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
              {personalized ? "Your audit ROI" : "Typical audit ROI"}
            </p>
            <h2 className="mt-4 font-heading text-[clamp(1.75rem,4vw,2.25rem)] leading-tight tracking-tight text-foreground">
              {buildPositiveRoiHeadline(metrics)}
            </h2>
            <p className="mt-3 max-w-2xl text-sm leading-relaxed text-muted-foreground">
              {personalized
                ? buildPositiveRoiSubhead(recoverableArr)
                : `Example: if you recover ${exampleAmount} in annual recurring revenue, a ${formatCurrency(VERIFICATION_REPORT_BASE_FEE_USD)} base fee plus 10% success fee often pays back quickly.`}
            </p>

            <dl className="mt-8 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-2 lg:grid-cols-4">
              {stats.map((stat) => (
                <div key={stat.label} className="bg-card px-5 py-5">
                  <dt className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    {stat.label}
                  </dt>
                  <dd className="mt-2 font-heading text-xl tracking-tight tnum text-foreground lg:text-2xl">
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
            <p className="mt-3 text-xs leading-relaxed text-muted-foreground">
              {personalized ? AUDIT_ROI_DISCLAIMER : `${AUDIT_ROI_DISCLAIMER} Example uses ${exampleAmount} recoverable ARR.`}
            </p>
          </div>
        </div>
      </HairlineCard>
    </Reveal>
  );
}
