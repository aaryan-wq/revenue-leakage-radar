import type { FindingResponse } from "@rlr/shared";
import { formatDecimal } from "@rlr/shared";

export function findingRecoverableArr(finding: FindingResponse): string {
  if (finding.recoverable_amount) {
    return finding.recoverable_amount;
  }
  return finding.estimated_arr_loss;
}

export function hasAffectedEntities(finding: FindingResponse): boolean {
  return Boolean(finding.customer_id || finding.subscription_id || finding.invoice_id);
}

function normalizeEvidenceKey(label: string): string {
  return label.toLowerCase().replace(/[\s_-]+/g, "");
}

export function summaryEvidencePairs(
  finding: FindingResponse,
  options?: { maxItems?: number },
): { label: string; value: string }[] {
  if (finding.attribution === "secondary") {
    return [];
  }

  const maxItems = options?.maxItems ?? 3;
  const seen = new Set<string>();
  const pairs: { label: string; value: string }[] = [];

  const addPair = (label: string, value: string) => {
    const normalized = normalizeEvidenceKey(label);
    if (seen.has(normalized) || !value || value === "-") {
      return;
    }
    seen.add(normalized);
    pairs.push({ label, value });
  };

  for (const record of finding.evidence_records) {
    if (pairs.length >= maxItems) {
      break;
    }
    const value =
      record.expected && record.actual
        ? `${formatDecimal(record.expected)} → ${formatDecimal(record.actual)}`
        : formatDecimal(record.actual ?? record.expected ?? "-");
    addPair(record.field, value);
  }

  for (const step of finding.calculation_trace?.steps ?? []) {
    if (pairs.length >= maxItems) {
      break;
    }
    addPair(step.label, formatDecimal(step.value));
  }

  return pairs;
}
