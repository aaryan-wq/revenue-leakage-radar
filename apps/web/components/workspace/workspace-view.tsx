"use client";

import { memo, useMemo, useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";

import { CountUp } from "@/components/count-up";
import {
  getSeverityDotClass,
  getSeverityLabel,
} from "@/components/findings/severity-utils";
import { glide } from "@/components/motion";
import { WORKSPACE_UPLOAD_HREF } from "@/lib/audit-session";
import { formatCurrency, formatDecimal, type FindingResponse } from "@rlr/shared";

function formatCompactCurrency(value: string | number): string {
  const amount = typeof value === "string" ? parseFloat(value) : value;
  if (Number.isNaN(amount)) return "$0";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(amount);
}

function findingDisplayId(finding: FindingResponse): string {
  return finding.rule_id || finding.id.slice(0, 8).toUpperCase();
}

function evidencePairs(
  finding: FindingResponse,
): { label: string; value: string }[] {
  return finding.evidence_records.slice(0, 3).map((record) => ({
    label: record.field,
    value:
      [record.expected, record.actual]
        .filter(Boolean)
        .map((part) => formatDecimal(part))
        .join(" → ") || "-",
  }));
}

interface WorkspaceViewProps {
  findings: FindingResponse[];
  reportId?: string | null;
}

const SidebarFindingButton = memo(function SidebarFindingButton({
  finding,
  selected,
  onSelect,
}: {
  finding: FindingResponse;
  selected: boolean;
  onSelect: (id: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onSelect(finding.id)}
      className="relative block w-full px-6 py-4 text-left md:px-8"
    >
      {selected && (
        <span className="absolute inset-y-1 left-0 w-[2px] bg-primary" />
      )}
      <div className="flex items-start gap-3">
        <span
          className={`mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full ${getSeverityDotClass(finding.severity)}`}
        />
        <div className="min-w-0 flex-1">
          <p
            className={`truncate text-[0.9rem] transition-colors ${
              selected ? "text-foreground" : "text-muted-foreground"
            }`}
          >
            {finding.title}
          </p>
          <p className="mt-0.5 text-xs text-muted-foreground tnum">
            {findingDisplayId(finding)} ·{" "}
            {formatCompactCurrency(finding.estimated_arr_loss)}
          </p>
        </div>
      </div>
    </button>
  );
});

export function WorkspaceView({ findings, reportId }: WorkspaceViewProps) {
  const sorted = useMemo(
    () =>
      [...findings].sort(
        (a, b) =>
          parseFloat(b.estimated_arr_loss) - parseFloat(a.estimated_arr_loss),
      ),
    [findings],
  );

  const [activeId, setActiveId] = useState(sorted[0]?.id ?? "");
  const [searchQuery, setSearchQuery] = useState("");

  const filtered = useMemo(() => {
    const query = searchQuery.trim().toLowerCase();
    if (!query) return sorted;
    return sorted.filter(
      (finding) =>
        finding.title.toLowerCase().includes(query) ||
        finding.category_label.toLowerCase().includes(query) ||
        findingDisplayId(finding).toLowerCase().includes(query),
    );
  }, [sorted, searchQuery]);

  if (sorted.length === 0) {
    return (
      <div className="px-6 py-16 text-center md:px-8">
        <p className="text-lg text-muted-foreground">No findings available yet.</p>
        <Link
          href={WORKSPACE_UPLOAD_HREF}
          className="mt-6 inline-flex rounded-full bg-primary px-5 py-2.5 text-[0.85rem] font-medium text-primary-foreground"
        >
          Run an audit
        </Link>
      </div>
    );
  }

  const active =
    sorted.find((finding) => finding.id === activeId) ??
    filtered.find((finding) => finding.id === activeId) ??
    sorted[0];
  const activeEvidence = evidencePairs(active);
  const showSearch = sorted.length > 30;

  return (
    <div className="grid gap-0 lg:grid-cols-[20rem_1fr]">
      <aside className="border-b border-line lg:border-b-0 lg:border-r">
        <div className="px-6 py-6 md:px-8">
          <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">
            Findings · {sorted.length}
          </p>
          {showSearch && (
            <input
              type="search"
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              placeholder="Filter findings…"
              aria-label="Filter findings"
              className="mt-4 w-full rounded-lg border border-line bg-secondary/30 px-3 py-2 text-sm outline-none transition-colors placeholder:text-muted-foreground focus:border-primary/40"
            />
          )}
        </div>
        <nav className="max-h-[min(70vh,40rem)] overflow-y-auto pb-4">
          {filtered.length === 0 ? (
            <p className="px-6 text-sm text-muted-foreground md:px-8">
              No findings match your search.
            </p>
          ) : (
            filtered.map((finding) => (
              <SidebarFindingButton
                key={finding.id}
                finding={finding}
                selected={finding.id === active.id}
                onSelect={setActiveId}
              />
            ))
          )}
        </nav>
      </aside>

      <section className="min-h-[40rem] px-6 py-10 md:px-12 md:py-14">
        <AnimatePresence mode="wait">
          <motion.div
            key={active.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.25, ease: glide }}
          >
            <div className="flex flex-wrap items-center gap-3">
              <span className="font-mono text-xs text-muted-foreground">
                {findingDisplayId(active)}
              </span>
              <span className="flex items-center gap-2 text-[0.72rem] uppercase tracking-[0.14em]">
                <span
                  className={`h-1.5 w-1.5 rounded-full ${getSeverityDotClass(active.severity)}`}
                />
                {getSeverityLabel(active.severity)}
              </span>
              <span className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                {active.category_label}
              </span>
            </div>

            <h2 className="mt-5 max-w-2xl font-heading text-[clamp(1.8rem,4vw,2.8rem)] leading-[1.05] tracking-tight text-balance">
              {active.title}
            </h2>

            <div className="mt-10 flex flex-wrap items-end gap-x-14 gap-y-8 border-y border-line py-10">
              <div>
                <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  Recoverable, annualized
                </p>
                <div className="mt-3 font-heading text-[clamp(2.6rem,6vw,4.4rem)] leading-none tracking-tight tnum">
                  <CountUp
                    key={active.id}
                    to={parseFloat(active.estimated_arr_loss) || 0}
                    prefix="$"
                    duration={1.4}
                  />
                </div>
              </div>
              <div className="flex gap-x-12 gap-y-6">
                <div>
                  <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Monthly
                  </p>
                  <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                    {formatCurrency(active.estimated_monthly_loss)}
                  </p>
                </div>
                <div>
                  <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                    Confidence
                  </p>
                  <p className="mt-3 font-heading text-2xl tracking-tight tnum">
                    {active.confidence}%
                  </p>
                </div>
              </div>
            </div>

            {activeEvidence.length > 0 && (
              <div className="mt-10">
                <p className="mb-5 text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                  Evidence
                </p>
                <div className="grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-3">
                  {activeEvidence.map((item) => (
                    <div key={item.label} className="bg-card px-5 py-6">
                      <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                        {item.label}
                      </p>
                      <p className="mt-2 font-heading text-xl tracking-tight tnum">
                        {item.value}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {active.recommendation && (
              <div className="mt-10 max-w-2xl border-l-2 border-primary/40 pl-5">
                <p className="text-[0.72rem] uppercase tracking-[0.12em] text-primary">
                  Recommended remedy
                </p>
                <p className="mt-2 text-lg leading-relaxed text-foreground">
                  {active.recommendation}
                </p>
              </div>
            )}

            <div className="mt-10 flex flex-wrap gap-3">
              <Link
                href={`/findings/${active.id}`}
                className="rounded-full bg-primary px-5 py-2.5 text-[0.85rem] font-medium text-primary-foreground transition-shadow hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50"
              >
                Open finding detail
              </Link>
              {reportId && (
                <Link
                  href={`/report/${reportId}`}
                  className="rounded-full border border-foreground/15 px-5 py-2.5 text-[0.85rem] transition-colors hover:bg-secondary"
                >
                  View full report
                </Link>
              )}
            </div>
          </motion.div>
        </AnimatePresence>
      </section>
    </div>
  );
}
