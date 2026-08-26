"use client";

import Link from "next/link";
import { Check, Copy, Link2 } from "lucide-react";
import { AnimatePresence, motion } from "framer-motion";

import { CountUp } from "@/components/count-up";
import {
  getSeverityDotClass,
  getSeverityLabel,
} from "@/components/findings/severity-utils";
import { AffectedEntities } from "@/components/findings/affected-entities";
import { ExcludedArrNotice } from "@/components/findings/excluded-arr-notice";
import {
  findingRecoverableArr,
  hasAffectedEntities,
} from "@/components/findings/finding-display-utils";
import { glide } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDecimal, type FindingDetailResponse } from "@rlr/shared";

function findingDisplayId(finding: FindingDetailResponse): string {
  return finding.rule_id || finding.id.slice(0, 8).toUpperCase();
}

export interface FindingDetailViewProps {
  finding: FindingDetailResponse;
  mode?: "live" | "demo";
  copied?: boolean;
  onCopyLink?: () => void;
  reportHref?: string;
  backLabel?: string;
  footer?: React.ReactNode;
}

export function FindingDetailView({
  finding,
  mode = "live",
  copied = false,
  onCopyLink,
  reportHref,
  backLabel = "Back to report",
  footer,
}: FindingDetailViewProps) {
  const isDemo = mode === "demo";
  const isSecondary = finding.attribution === "secondary";
  const recoverableArr = findingRecoverableArr(finding);
  const resolvedReportHref = reportHref ?? (finding.report_id ? `/report/${finding.report_id}` : null);

  return (
    <div className="mx-auto max-w-report px-6 py-16 md:px-10 md:py-20">
      <AnimatePresence mode="wait">
        <motion.div
          key={finding.id}
          initial={{ opacity: 0, y: 16, filter: "blur(6px)" }}
          animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
          exit={{ opacity: 0, y: -10, filter: "blur(6px)" }}
          transition={{ duration: 0.6, ease: glide }}
        >
          <div className="flex flex-wrap items-start justify-between gap-6">
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-xs text-muted-foreground">
                {findingDisplayId(finding)}
              </span>
              <span className="flex items-center gap-2 text-[0.72rem] uppercase tracking-[0.14em]">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${getSeverityDotClass(finding.severity)}`}
                />
                {getSeverityLabel(finding.severity)}
              </span>
              <span className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                {finding.category_label}
              </span>
            </div>
            <div className="flex gap-3">
              {onCopyLink && (
                <Button variant="secondary" size="sm" onClick={() => void onCopyLink()}>
                  {copied ? (
                    <>
                      <Check className="mr-2 h-4 w-4" strokeWidth={1.75} />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="mr-2 h-4 w-4" strokeWidth={1.75} />
                      Copy Link
                    </>
                  )}
                </Button>
              )}
              {resolvedReportHref && (
                <Link href={resolvedReportHref}>
                  <Button variant="ghost" size="sm">
                    <Link2 className="mr-2 h-4 w-4" strokeWidth={1.75} />
                    View Report
                  </Button>
                </Link>
              )}
            </div>
          </div>

          <h1 className="mt-5 max-w-2xl font-heading text-[clamp(1.8rem,4vw,2.8rem)] leading-[1.05] tracking-tight text-balance">
            {finding.title}
          </h1>

          {hasAffectedEntities(finding) && (
            <AffectedEntities finding={finding} className="mt-8" />
          )}

          <div className="mt-10 flex flex-wrap items-end gap-x-14 gap-y-8 border-y border-line py-10">
            <div>
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                {isSecondary ? "Excluded ARR" : "Recoverable, annualized"}
              </p>
              <div
                className={`mt-3 font-heading text-[clamp(2.6rem,6vw,4.4rem)] leading-none tracking-tight tnum ${
                  isSecondary ? "text-muted-foreground" : ""
                }`}
              >
                <CountUp
                  to={parseFloat(recoverableArr) || 0}
                  prefix="$"
                  duration={1.4}
                />
              </div>
              {isSecondary && <ExcludedArrNotice finding={finding} className="mt-4" />}
            </div>
            <div className="flex gap-x-12 gap-y-6">
              <div>
                <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  {isSecondary ? "Headline impact" : "Monthly"}
                </p>
                <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                  {isSecondary
                    ? "Not counted"
                    : formatCurrency(finding.estimated_monthly_loss)}
                </p>
              </div>
              <div>
                <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  Confidence
                </p>
                <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                  {finding.confidence}%
                </p>
              </div>
            </div>
          </div>

          {finding.recommendation && (
            <div className="mt-10 max-w-2xl border-l-2 border-primary/40 pl-5">
              <p className="text-[0.72rem] uppercase tracking-[0.12em] text-primary">
                Recommended remedy
              </p>
              <p className="mt-2 text-lg leading-relaxed text-foreground">
                {finding.recommendation}
              </p>
            </div>
          )}

          <div className="mt-10">
            <p className="mb-5 text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
              Evidence
            </p>
            {finding.evidence_records.length > 0 ? (
              <div className="overflow-x-auto rounded-xl border border-line">
                <table className="w-full min-w-[720px] text-left text-sm">
                  <thead>
                    <tr className="border-b border-line text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                      <th className="px-5 py-4 font-medium">Field</th>
                      <th className="px-5 py-4 font-medium">Expected</th>
                      <th className="px-5 py-4 font-medium">Actual</th>
                      <th className="px-5 py-4 font-medium">References</th>
                    </tr>
                  </thead>
                  <tbody>
                    {finding.evidence_records.map((record, index) => (
                      <tr key={index} className="border-b border-line last:border-b-0">
                        <td className="px-5 py-4 text-foreground">{record.field}</td>
                        <td className="px-5 py-4 tnum text-muted-foreground">
                          {formatDecimal(record.expected ?? "-")}
                        </td>
                        <td className="px-5 py-4 tnum text-foreground">
                          {formatDecimal(record.actual ?? "-")}
                        </td>
                        <td className="px-5 py-4 text-xs text-muted-foreground">
                          {record.reference_ids
                            ? Object.entries(record.reference_ids)
                                .map(([key, value]) => `${key}: ${value}`)
                                .join(", ")
                            : "-"}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <p className="text-sm text-muted-foreground">No detailed evidence records.</p>
            )}
          </div>

          {footer ?? (
            <div className="mt-10 flex flex-wrap gap-4">
              {resolvedReportHref && (
                <Link
                  href={resolvedReportHref}
                  className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                >
                  ← {backLabel}
                </Link>
              )}
              {!isDemo && (
                <Link
                  href="/dashboard"
                  className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                >
                  Open workspace
                </Link>
              )}
            </div>
          )}
        </motion.div>
      </AnimatePresence>
    </div>
  );
}
