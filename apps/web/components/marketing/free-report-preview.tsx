"use client";

import Link from "next/link";
import { Lock } from "lucide-react";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { GlassCard } from "@/components/ui/glass-card";
import { formatCurrency } from "@rlr/shared";

const SAMPLE_FINDINGS = [
  {
    id: "RLR-001",
    title: "Legacy pricing on enterprise tier",
    category: "Legacy Pricing",
    confidence: 0.94,
    annualized: 48_000,
  },
  {
    id: "RLR-002",
    title: "Expired discount still applied",
    category: "Expired Discount",
    confidence: 0.91,
    annualized: 12_400,
  },
  {
    id: "RLR-003",
    title: "Renewal price below contract terms",
    category: "Renewal Drift",
    confidence: 0.88,
    annualized: 31_200,
  },
] as const;

const LOCKED_CARDS = [
  { title: "Duplicate discount stacking", category: "Duplicate Discount", arr: 18_600 },
  { title: "Invoice line item off catalog", category: "Price Catalog Mismatch", arr: 9_800 },
  { title: "Seat count variance detected", category: "Seat Count Variance", arr: 14_200 },
] as const;

interface FreeReportPreviewProps {
  variant?: "compact" | "full";
  showCta?: boolean;
}

export function FreeReportPreview({ variant = "full", showCta = true }: FreeReportPreviewProps) {
  const isCompact = variant === "compact";

  return (
    <section className={isCompact ? "mt-16 border-t border-line pt-16" : "border-t border-line bg-secondary/40"}>
      <div className={isCompact ? "" : "mx-auto max-w-marketing px-6 py-20 md:px-10 md:py-24"}>
        <Reveal>
          <p className="mb-3 text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">
            Your free report
          </p>
          <h2 className="max-w-xl font-heading text-[clamp(1.6rem,3.5vw,2.4rem)] leading-[1.05] tracking-tight text-balance">
            {isCompact
              ? "Every upload includes a free executive summary."
              : "See recoverable revenue before you pay for anything."}
          </h2>
          <p className="mt-4 max-w-2xl text-pretty leading-relaxed text-muted-foreground">
            After your scan completes, you receive a free summary with total recoverable ARR,
            confidence scores, and a preview of top findings. Customer names and invoice evidence
            stay locked until you unlock the full report.
          </p>
        </Reveal>

        <Stagger className="mt-12">
          <div className="grid grid-cols-[1fr_auto] items-center gap-4 border-b border-line pb-3 text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground md:grid-cols-[auto_1fr_auto_auto]">
            <span className="hidden md:block">Ref</span>
            <span>Finding</span>
            <span className="hidden text-right md:block">Confidence</span>
            <span className="text-right">Annualized</span>
          </div>
          {SAMPLE_FINDINGS.map((finding) => (
            <StaggerItem key={finding.id} y={14}>
              <div className="grid grid-cols-[1fr_auto] items-center gap-4 border-b border-line py-4 transition-colors hover:bg-background/50 md:grid-cols-[auto_1fr_auto_auto]">
                <span className="hidden font-mono text-xs text-muted-foreground md:block">
                  {finding.id}
                </span>
                <div className="min-w-0">
                  <p className="truncate text-[0.98rem] text-foreground">{finding.title}</p>
                  <p className="mt-0.5 text-xs uppercase tracking-wider text-muted-foreground">
                    {finding.category}
                  </p>
                </div>
                <span className="hidden text-right text-sm text-muted-foreground tnum md:block">
                  {Math.round(finding.confidence * 100)}%
                </span>
                <span className="text-right font-heading text-lg tracking-tight tnum">
                  {formatCurrency(finding.annualized)}
                </span>
              </div>
            </StaggerItem>
          ))}
        </Stagger>

        <Reveal delay={0.1} className="mt-10">
          <div className="flex items-center gap-3">
            <Lock className="h-5 w-5 text-muted-foreground" strokeWidth={1.75} />
            <h3 className="font-heading text-xl tracking-tight text-foreground">
              Detailed findings preview
            </h3>
          </div>
          <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
            Unlock the full report to view customer names, invoice evidence, and remediation steps.
          </p>
        </Reveal>

        <Stagger className="mt-8 grid gap-4 md:grid-cols-3">
          {LOCKED_CARDS.map((item) => (
            <StaggerItem key={item.title}>
              <GlassCard padding="sm" subtle className="relative overflow-hidden">
                <div className="select-none blur-sm">
                  <p className="text-sm font-medium text-foreground">{item.title}</p>
                  <p className="mt-2 text-sm text-muted-foreground">{item.category}</p>
                  <p className="mt-4 font-heading text-xl tracking-tight tnum">
                    {formatCurrency(item.arr)}
                  </p>
                </div>
                <div className="absolute inset-0 flex items-center justify-center bg-card/70 backdrop-blur-sm">
                  <Lock className="h-6 w-6 text-muted-foreground" strokeWidth={1.75} />
                </div>
              </GlassCard>
            </StaggerItem>
          ))}
        </Stagger>

        {showCta && (
          <Reveal delay={0.15} className="mt-10 flex flex-wrap items-center gap-4">
            <p className="text-sm text-muted-foreground">
              Customer names blurred in free summary. Unlock for full evidence.
            </p>
            <Link
              href="/pricing"
              className="inline-flex items-center gap-2 rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem] transition-colors hover:bg-foreground hover:text-background"
            >
              View pricing →
            </Link>
          </Reveal>
        )}
      </div>
    </section>
  );
}
