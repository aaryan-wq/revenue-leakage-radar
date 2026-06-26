"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import { motion, AnimatePresence } from "framer-motion";
import { ChevronDown } from "lucide-react";

import { SeverityBadge } from "@/components/findings/severity-badge";
import { GlassCard } from "@/components/ui/glass-card";
import { formatCurrency, type FindingResponse } from "@rlr/shared";

interface FindingsTableProps {
  findings: FindingResponse[];
}

type SortKey = "arr" | "confidence" | "category";

export function FindingsTable({ findings }: FindingsTableProps) {
  const [sortKey, setSortKey] = useState<SortKey>("arr");
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [severityFilter, setSeverityFilter] = useState<string | null>(null);
  const [categoryFilter, setCategoryFilter] = useState<string | null>(null);

  const severities = useMemo(
    () => [...new Set(findings.map((f) => f.severity))].sort(),
    [findings],
  );
  const categories = useMemo(
    () => [...new Set(findings.map((f) => f.category_label))].sort(),
    [findings],
  );

  const sorted = useMemo(() => {
    let copy = [...findings];
    if (severityFilter) {
      copy = copy.filter((f) => f.severity === severityFilter);
    }
    if (categoryFilter) {
      copy = copy.filter((f) => f.category_label === categoryFilter);
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

  if (findings.length === 0) {
    return (
      <GlassCard padding="md">
        <p className="text-body text-gray-500">No findings in this report.</p>
      </GlassCard>
    );
  }

  return (
    <GlassCard padding="md">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h3 className="text-h3 font-semibold text-gray-900">Findings</h3>
          <p className="mt-1 text-body text-gray-500">
            {sorted.length} of {findings.length} evidence-backed issues
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <SortButton active={sortKey === "arr"} onClick={() => setSortKey("arr")}>
            Highest ARR
          </SortButton>
          <SortButton active={sortKey === "confidence"} onClick={() => setSortKey("confidence")}>
            Confidence
          </SortButton>
          <SortButton active={sortKey === "category"} onClick={() => setSortKey("category")}>
            Category
          </SortButton>
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
            onClick={() => setSeverityFilter(severityFilter === severity ? null : severity)}
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
            onClick={() => setCategoryFilter(categoryFilter === category ? null : category)}
          />
        ))}
      </div>

      <div className="mt-8 space-y-4">
        {sorted.map((finding) => {
          const isExpanded = expandedId === finding.id;
          return (
            <article key={finding.id} className="glass-subtle overflow-hidden rounded-card">
              <button
                type="button"
                className="focus-ring flex w-full items-start justify-between gap-4 p-6 text-left transition-colors hover:bg-surface-glass-subtle"
                onClick={() => setExpandedId(isExpanded ? null : finding.id)}
              >
                <div className="min-w-0 flex-1">
                  <div className="flex flex-wrap items-center gap-3">
                    <SeverityBadge severity={finding.severity} />
                    <span className="text-small text-gray-500">{finding.category_label}</span>
                  </div>
                  <Link
                    href={`/findings/${finding.id}`}
                    className="mt-3 block text-body font-medium text-gray-900 hover:text-primary hover:underline"
                    onClick={(e) => e.stopPropagation()}
                  >
                    {finding.title}
                  </Link>
                  <p className="mt-2 text-h4 font-semibold tabular-nums text-gray-900">
                    {formatCurrency(finding.estimated_arr_loss)}
                    <span className="ml-2 text-small font-normal text-gray-500">ARR</span>
                  </p>
                </div>
                <div className="flex items-center gap-3 text-gray-400">
                  <span className="text-small tabular-nums">{finding.confidence}%</span>
                  <motion.span
                    animate={{ rotate: isExpanded ? 180 : 0 }}
                    transition={{ duration: 0.2 }}
                  >
                    <ChevronDown className="h-5 w-5" strokeWidth={1.75} />
                  </motion.span>
                </div>
              </button>

              <AnimatePresence initial={false}>
                {isExpanded && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
                    className="overflow-hidden"
                  >
                    <div className="border-t border-border px-6 py-6">
                      <div className="mb-6 grid gap-4 sm:grid-cols-3">
                        <div>
                          <p className="text-caption text-gray-500">Monthly Impact</p>
                          <p className="mt-1 tabular-nums text-body text-gray-900">
                            {formatCurrency(finding.estimated_monthly_loss)}
                          </p>
                        </div>
                        <div>
                          <p className="text-caption text-gray-500">Annual Impact</p>
                          <p className="mt-1 tabular-nums text-body text-gray-900">
                            {formatCurrency(finding.estimated_arr_loss)}
                          </p>
                        </div>
                        {finding.customer_id && (
                          <div>
                            <p className="text-caption text-gray-500">Customer</p>
                            <p className="mt-1 text-body text-gray-900">{finding.customer_id}</p>
                          </div>
                        )}
                      </div>
                      {finding.recommendation && (
                        <div className="mb-6">
                          <p className="text-overline uppercase text-gray-500">Recommendation</p>
                          <p className="mt-2 text-body text-gray-700">{finding.recommendation}</p>
                        </div>
                      )}
                      {finding.evidence_records.length > 0 ? (
                        <div className="overflow-x-auto">
                          <table className="w-full min-w-[560px] text-left text-small">
                            <thead>
                              <tr className="border-b border-border text-caption text-gray-500">
                                <th className="pb-3 pr-4 font-medium">Field</th>
                                <th className="pb-3 pr-4 font-medium">Expected</th>
                                <th className="pb-3 font-medium">Actual</th>
                              </tr>
                            </thead>
                            <tbody>
                              {finding.evidence_records.map((record, index) => (
                                <tr key={index} className="border-b border-border">
                                  <td className="py-3 pr-4 text-gray-900">{record.field}</td>
                                  <td className="py-3 pr-4 tabular-nums text-gray-700">
                                    {record.expected ?? "—"}
                                  </td>
                                  <td className="py-3 tabular-nums text-gray-700">
                                    {record.actual ?? "—"}
                                  </td>
                                </tr>
                              ))}
                            </tbody>
                          </table>
                        </div>
                      ) : (
                        <p className="text-small text-gray-500">No detailed evidence records.</p>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </article>
          );
        })}
      </div>
    </GlassCard>
  );
}

function SortButton({
  active,
  onClick,
  children,
}: {
  active: boolean;
  onClick: () => void;
  children: React.ReactNode;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`focus-ring rounded-button border px-3 py-2 text-small transition-all duration-fast ${
        active
          ? "border-primary bg-primary text-white"
          : "glass-subtle border-border text-gray-600 hover:border-border-strong"
      }`}
    >
      {children}
    </button>
  );
}

function FilterChip({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`focus-ring rounded-pill border px-3 py-1.5 text-caption capitalize transition-all ${
        active
          ? "border-primary bg-primary text-white"
          : "border-border text-gray-600 hover:border-border-strong"
      }`}
    >
      {label}
    </button>
  );
}
