import type { AuditStatus, ReportListItem } from "@rlr/shared";

export type AuditSortKey = "date" | "status" | "arr" | "access" | "findings";
export type SortDirection = "asc" | "desc";

export const DEFAULT_AUDIT_SORT_KEY: AuditSortKey = "date";
export const DEFAULT_AUDIT_SORT_DIRECTION: SortDirection = "desc";

const DEFAULT_DIRECTION: Record<AuditSortKey, SortDirection> = {
  date: "desc",
  status: "asc",
  arr: "desc",
  access: "desc",
  findings: "desc",
};

const STATUS_RANK: Record<AuditStatus, number> = {
  completed: 0,
  generating_report: 1,
  scanning: 2,
  ready_for_scan: 3,
  normalizing: 4,
  validating: 5,
  mapping: 6,
  uploading: 7,
  created: 8,
  payment_pending: 9,
  validation_failed: 10,
  processing_failed: 11,
  upload_failed: 12,
};

function compareValues(
  left: number | string,
  right: number | string,
  direction: SortDirection,
): number {
  const delta =
    typeof left === "number" && typeof right === "number"
      ? left - right
      : String(left).localeCompare(String(right), undefined, { sensitivity: "base" });
  return direction === "asc" ? delta : -delta;
}

export function nextAuditSort(
  currentKey: AuditSortKey,
  currentDirection: SortDirection,
  nextKey: AuditSortKey,
): { key: AuditSortKey; direction: SortDirection } {
  if (currentKey === nextKey) {
    return { key: nextKey, direction: currentDirection === "asc" ? "desc" : "asc" };
  }
  return { key: nextKey, direction: DEFAULT_DIRECTION[nextKey] };
}

export function sortAudits(
  audits: ReportListItem[],
  sortKey: AuditSortKey,
  direction: SortDirection,
): ReportListItem[] {
  return [...audits].sort((a, b) => {
    switch (sortKey) {
      case "date": {
        const left = a.date ? new Date(a.date).getTime() : 0;
        const right = b.date ? new Date(b.date).getTime() : 0;
        return compareValues(left, right, direction);
      }
      case "status": {
        const left = STATUS_RANK[a.status] ?? 99;
        const right = STATUS_RANK[b.status] ?? 99;
        return compareValues(left, right, direction);
      }
      case "arr": {
        const left = Number.parseFloat(a.recoverable_arr || "0");
        const right = Number.parseFloat(b.recoverable_arr || "0");
        return compareValues(left, right, direction);
      }
      case "access": {
        const left = a.purchased ? 1 : 0;
        const right = b.purchased ? 1 : 0;
        return compareValues(left, right, direction);
      }
      case "findings":
        return compareValues(a.finding_count, b.finding_count, direction);
      default:
        return 0;
    }
  });
}

export function sortAuditsByDate<T extends { date: string | null }>(audits: T[]): T[] {
  return [...audits].sort((a, b) => {
    const left = a.date ? new Date(a.date).getTime() : 0;
    const right = b.date ? new Date(b.date).getTime() : 0;
    return right - left;
  });
}
