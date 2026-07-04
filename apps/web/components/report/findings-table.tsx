"use client";

import { memo, useEffect, useMemo, useState } from "react";
import Link from "next/link";

import { SeverityBadge } from "@/components/findings/severity-badge";
import { ExcludedArrNotice } from "@/components/findings/excluded-arr-notice";
import {
  findingRecoverableArr,
  summaryEvidencePairs,
} from "@/components/findings/finding-display-utils";
import { Button } from "@/components/ui/button";
import { formatCurrency, formatDecimal, type FindingResponse } from "@rlr/shared";

const PAGE_SIZE = 25;

interface FindingsTableProps {
  findings: FindingResponse[];
}

type SortKey = "arr" | "confidence" | "category";

function findingDisplayId(finding: FindingResponse): string {
  return finding.rule_id || finding.id.slice(0, 8).toUpperCase();
}

const FindingRow = memo(function FindingRow({
  finding,
}: {
  finding: FindingResponse;
}) {
  const evidence = summaryEvidencePairs(finding);
  const isSecondary = finding.attribution === "secondary";
  const displayArr = findingRecoverableArr(finding);

  return (
    <article className="grid gap-8 border-t border-line py-12 md:grid-cols-[1fr_auto]">
      <div className="max-w-2xl">
        <div className="mb-3 flex flex-wrap items-center gap-3">
          <span className="font-mono text-xs text-muted-foreground">
            {findingDisplayId(finding)}
          </span>
          <SeverityBadge severity={finding.severity} />
          {isSecondary && (
            <span className="rounded-full border border-line px-2 py-0.5 text-[0.65rem] uppercase tracking-[0.1em] text-muted-foreground">
              Secondary overlap
            </span>
          )}
          <span className="h-1 w-1 rounded-full bg-muted-foreground/40" />
          <span className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
            {finding.category_label}
          </span>
        </div>
        <Link
          href={`/findings/${finding.id}`}
          className="font-heading text-2xl leading-snug tracking-tight text-balance transition-colors hover:text-primary"
        >
          {finding.title}
        </Link>

        {isSecondary && <ExcludedArrNotice finding={finding} className="mt-4" />}

        {evidence.length > 0 && (
          <div className="mt-7 flex flex-wrap gap-x-10 gap-y-3">
            {evidence.map((item) => (
              <div key={item.label}>
                <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
                  {item.label}
                </p>
                <p className="mt-1 text-sm text-foreground tnum">{formatDecimal(item.value)}</p>
              </div>
            ))}
          </div>
        )}

        {finding.recommendation && (
          <div className="mt-7 border-l-2 border-primary/40 pl-4">
            <p className="text-[0.72rem] uppercase tracking-[0.12em] text-primary">
              Recommended remedy
            </p>
            <p className="mt-1.5 leading-relaxed text-foreground">
              {finding.recommendation}
            </p>
          </div>
        )}
      </div>
      <div className="text-right md:min-w-[10rem]">
        <p className="text-[0.7rem] uppercase tracking-[0.12em] text-muted-foreground">
          {isSecondary ? "Excluded ARR" : "Annualized"}
        </p>
        <p
          className={`mt-2 font-heading text-3xl tracking-tight tnum ${
            isSecondary ? "text-muted-foreground" : ""
          }`}
        >
          {isSecondary ? formatCurrency(displayArr) : formatCurrency(finding.estimated_arr_loss)}
        </p>
        {finding.leakage_computation && (
          <p className="mt-2 text-xs text-muted-foreground tnum">
            {formatCurrency(finding.leakage_computation.monthly_loss)}/mo · qty{" "}
            {formatDecimal(finding.leakage_computation.quantity, 0)}
          </p>
        )}
        <p className="mt-3 text-xs text-muted-foreground tnum">
          {formatDecimal(finding.confidence, 0)}% conf.
        </p>
      </div>
    </article>
  );
});

export function FindingsTable({ findings }: FindingsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("arr");
  const [severityFilter, setSeverityFilter] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);

  const severities = useMemo(
    () => [...new Set(findings.map((finding) => finding.severity))].sort(),
    [findings],
  );
  const categories = useMemo(
    () => [...new Set(findings.map((finding) => finding.category_label))].sort(),
    [findings],
  );

  const sorted = useMemo(() => {
    let copy = [...findings];
    if (severityFilter) {
      copy = copy.filter((finding) => finding.severity === severityFilter);
    }
    if (categoryFilter) {
      copy = copy.filter((finding) => finding.category_label === categoryFilter);
    }
    copy.sort((a, b) => {
      if (sortKey === "arr") {
        return parseFloat(b.estimated_arr_loss) - parseFloat(a.estimated_arr_loss);
      }
      if (sortKey === "confidence") {
        return parseFloat(b.confidence) - parseFloat(a.confidence);
      }
      return a.category_label.localeCompare(b.category_label);
    });
    return copy;
  }, [findings, sortKey, severityFilter, categoryFilter]);

  useEffect(() => {
    setVisibleCount(PAGE_SIZE);
  }, [sortKey, severityFilter, categoryFilter, findings]);

  const visible = sorted.slice(0, visibleCount);
  const hasMore = visibleCount < sorted.length;

  if (findings.length === 0) {
    return (
      <p className="text-sm leading-relaxed text-muted-foreground">
        No findings in this report.
      </p>
    );
  }

  return (
    <div>
      <div className="flex flex-wrap items-center justify-between gap-4">
        <p className="text-sm text-muted-foreground">
          {sorted.length} of {findings.length} evidence-backed issues
        </p>
        <div className="flex flex-wrap gap-2">
          <FilterChip active={sortKey === "arr"} onClick={() => setSortKey("arr")}>
            Highest ARR
          </FilterChip>
          <FilterChip
            active={sortKey === "confidence"}
            onClick={() => setSortKey("confidence")}
          >
            Confidence
          </FilterChip>
          <FilterChip
            active={sortKey === "category"}
            onClick={() => setSortKey("category")}
          >
            Category
          </FilterChip>
        </div>
      </div>

      <div className="mt-6 flex flex-wrap gap-2">
        <FilterChip
          label="All severities"
          active={!severityFilter}
          onClick={() => setSeverityFilter(null)}
        />
        {severities.map((severity) => (
          <FilterChip
            key={severity}
            label={severity}
            active={severityFilter === severity}
            onClick={() =>
              setSeverityFilter(severityFilter === severity ? null : severity)
            }
          />
        ))}
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        <FilterChip
          label="All categories"
          active={!categoryFilter}
          onClick={() => setCategoryFilter(null)}
        />
        {categories.map((category) => (
          <FilterChip
            key={category}
            label={category}
            active={categoryFilter === category}
            onClick={() =>
              setCategoryFilter(categoryFilter === category ? null : category)
            }
          />
        ))}
      </div>

      <div className="mt-16">
        {visible.map((finding) => (
          <FindingRow key={finding.id} finding={finding} />
        ))}
      </div>

      {hasMore && (
        <div className="mt-8 flex flex-col items-center gap-3 border-t border-line pt-8">
          <p className="text-sm text-muted-foreground">
            Showing {visible.length} of {sorted.length} findings
          </p>
          <Button
            variant="secondary"
            onClick={() => setVisibleCount((count) => count + PAGE_SIZE)}
          >
            Load {Math.min(PAGE_SIZE, sorted.length - visible.length)} more
          </Button>
        </div>
      )}

      {!hasMore && (
        <p className="mt-4 border-t border-line pt-8 text-sm text-muted-foreground">
          Showing {sorted.length} finding{sorted.length === 1 ? "" : "s"} ranked by
          recoverable impact.
        </p>
      )}
    </div>
  );
}

function FilterChip({
  label,
  active,
  onClick,
  children,
}: {
  label?: string;
  active: boolean;
  onClick: () => void;
  children?: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full border px-3 py-1.5 text-[0.72rem] uppercase tracking-[0.08em] capitalize transition-colors ${
        active
          ? "border-primary bg-primary text-primary-foreground"
          : "border-line text-muted-foreground hover:border-foreground/20 hover:text-foreground"
      }`}
    >
      {children ?? label}
    </button>
  );
}
