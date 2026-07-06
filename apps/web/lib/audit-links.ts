import type { ReportListItem } from "@rlr/shared";

export function getAuditOpenHref(audit: Pick<ReportListItem, "audit_id" | "report_id" | "purchased">): string {
  return audit.purchased ? `/report/${audit.report_id}` : `/audits/${audit.audit_id}`;
}
