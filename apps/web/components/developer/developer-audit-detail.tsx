"use client";

import Link from "next/link";
import { useQuery } from "@tanstack/react-query";

import { Badge } from "@/components/ui/badge";
import { Button, buttonVariants } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { DeveloperDetailField, DeveloperDetailSection } from "@/components/developer/developer-detail-field";
import { getAdminAuditDetail } from "@/lib/admin-api";
import { useAppAuth } from "@/lib/app-auth";
import { ApiError } from "@/lib/api";
import { formatDeveloperTimestamp, formatDeveloperValue } from "@/lib/developer-format";
import { formatAuditStatusLabel } from "@/lib/format-audit-status";
import { queryKeys } from "@/lib/query/keys";
import { formatCurrency } from "@rlr/shared";

export function DeveloperAuditDetail({ auditId }: { auditId: string }) {
  const { getToken } = useAppAuth();

  const auditQuery = useQuery({
    queryKey: queryKeys.adminAudit(auditId),
    queryFn: async () => {
      const token = await getToken();
      if (!token) throw new ApiError("Authentication required.", 401);
      return getAdminAuditDetail(token, auditId);
    },
  });

  if (auditQuery.isLoading) {
    return <PageLoadingSkeleton message="Loading audit details…" variant="list" />;
  }

  if (auditQuery.error || !auditQuery.data) {
    const message =
      auditQuery.error instanceof ApiError ? auditQuery.error.message : "Unable to load audit.";
    return (
      <div className="rounded-2xl border border-line/60 bg-secondary/30 p-8 text-center">
        <p className="text-muted-foreground">{message}</p>
        <div className="mt-4 flex justify-center gap-3">
          <Link href="/developer/audits" className={buttonVariants({ variant: "secondary" })}>
            Back to audits
          </Link>
          <Button onClick={() => void auditQuery.refetch()}>Retry</Button>
        </div>
      </div>
    );
  }

  const audit = auditQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <Link
            href="/developer/audits"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Back to audits
          </Link>
          <h1 className="mt-2 font-heading text-2xl tracking-tight">
            {audit.company_name ?? "Audit detail"}
          </h1>
          <p className="mt-1 font-mono text-xs text-muted-foreground">{audit.audit_id}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Badge variant="gray">{formatAuditStatusLabel(audit.status)}</Badge>
          {audit.purchased && <Badge variant="elevated">Purchased</Badge>}
          {audit.is_anonymous && <Badge variant="gray">Anonymous</Badge>}
        </div>
      </div>

      <GlassCard className="space-y-8 p-8">
        <DeveloperDetailSection title="Overview">
          <dl className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <DeveloperDetailField label="Status" value={formatAuditStatusLabel(audit.status)} />
            <DeveloperDetailField
              label="Recoverable ARR"
              value={audit.recoverable_arr ? formatCurrency(audit.recoverable_arr) : "—"}
            />
            <DeveloperDetailField label="Findings" value={formatDeveloperValue(audit.finding_count)} />
            <DeveloperDetailField label="Platform" value={formatDeveloperValue(audit.platform)} />
            <DeveloperDetailField label="Audit type" value={formatDeveloperValue(audit.audit_type)} />
            <DeveloperDetailField label="Data tier" value={formatDeveloperValue(audit.data_tier)} />
            <DeveloperDetailField
              label="Created"
              value={formatDeveloperTimestamp(audit.created_at)}
            />
            <DeveloperDetailField
              label="Upload completed"
              value={formatDeveloperTimestamp(audit.upload_completed_at)}
            />
            <DeveloperDetailField
              label="Verification completed"
              value={formatDeveloperTimestamp(audit.verification_completed_at)}
            />
          </dl>
        </DeveloperDetailSection>

        <DeveloperDetailSection title="User">
          <dl className="grid gap-6 sm:grid-cols-2">
            <DeveloperDetailField
              label="Name"
              value={formatDeveloperValue(audit.clerk_user_name ?? "Anonymous")}
            />
            <DeveloperDetailField
              label="Email"
              value={formatDeveloperValue(audit.clerk_user_email)}
            />
            <DeveloperDetailField label="Clerk user ID" value={audit.clerk_user_id ?? "—"} mono />
          </dl>
        </DeveloperDetailSection>

        <DeveloperDetailSection title="Detection and coverage">
          <dl className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3">
            <DeveloperDetailField
              label="Billing platform"
              value={formatDeveloperValue(audit.billing_platform_detected)}
            />
            <DeveloperDetailField
              label="CRM platform"
              value={formatDeveloperValue(audit.crm_platform_detected)}
            />
            <DeveloperDetailField label="CSV files" value={formatDeveloperValue(audit.csv_file_count)} />
            <DeveloperDetailField
              label="Monthly leakage"
              value={
                audit.estimated_monthly_leakage
                  ? formatCurrency(audit.estimated_monthly_leakage)
                  : "—"
              }
            />
            <DeveloperDetailField
              label="Annual leakage"
              value={
                audit.estimated_annual_leakage
                  ? formatCurrency(audit.estimated_annual_leakage)
                  : "—"
              }
            />
            <DeveloperDetailField label="Coverage score" value={formatDeveloperValue(audit.coverage_score)} />
            <DeveloperDetailField
              label="Confidence score"
              value={formatDeveloperValue(audit.confidence_score)}
            />
            <DeveloperDetailField label="Rules executed" value={formatDeveloperValue(audit.rules_executed)} />
            <DeveloperDetailField label="Findings total" value={formatDeveloperValue(audit.findings_total)} />
          </dl>
        </DeveloperDetailSection>

        {(audit.ingestion_error || audit.scan_error || audit.validation_result) && (
          <DeveloperDetailSection title="Errors and validation">
            <dl className="grid gap-6">
              <DeveloperDetailField
                label="Validation result"
                value={formatDeveloperValue(audit.validation_result)}
              />
              <DeveloperDetailField
                label="Ingestion error"
                value={formatDeveloperValue(audit.ingestion_error)}
              />
              <DeveloperDetailField label="Scan error" value={formatDeveloperValue(audit.scan_error)} />
            </dl>
          </DeveloperDetailSection>
        )}

        <DeveloperDetailSection title="Links">
          <div className="flex flex-wrap gap-3">
            {audit.report_id && (
              <Link href={`/report/${audit.report_id}`} className={buttonVariants({ variant: "secondary" })}>
                View report
              </Link>
            )}
            {audit.assessment_id && (
              <Link
                href={`/developer/assessments/${audit.assessment_id}`}
                className={buttonVariants({ variant: "secondary" })}
              >
                View assessment
              </Link>
            )}
          </div>
        </DeveloperDetailSection>

        <DeveloperDetailSection title="Uploads">
          {audit.uploads.length === 0 ? (
            <p className="text-sm text-muted-foreground">No uploads recorded.</p>
          ) : (
            <div className="overflow-x-auto rounded-xl border border-line/60">
              <table className="min-w-full text-sm">
                <thead className="border-b border-line/60 bg-secondary/20 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">File</th>
                    <th className="px-4 py-3 font-medium">Type</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Uploaded</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.uploads.map((upload) => (
                    <tr key={upload.id} className="border-b border-line/40 last:border-0">
                      <td className="px-4 py-3">{upload.original_filename}</td>
                      <td className="px-4 py-3">{upload.file_type}</td>
                      <td className="px-4 py-3">{upload.status}</td>
                      <td className="px-4 py-3 tabular-nums">
                        {formatDeveloperTimestamp(upload.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </DeveloperDetailSection>

        {audit.purchases.length > 0 && (
          <DeveloperDetailSection title="Purchases">
            <div className="overflow-x-auto rounded-xl border border-line/60">
              <table className="min-w-full text-sm">
                <thead className="border-b border-line/60 bg-secondary/20 text-left">
                  <tr>
                    <th className="px-4 py-3 font-medium">Plan</th>
                    <th className="px-4 py-3 font-medium">Status</th>
                    <th className="px-4 py-3 font-medium">Amount</th>
                    <th className="px-4 py-3 font-medium">Created</th>
                  </tr>
                </thead>
                <tbody>
                  {audit.purchases.map((purchase) => (
                    <tr key={purchase.id} className="border-b border-line/40 last:border-0">
                      <td className="px-4 py-3">{purchase.plan}</td>
                      <td className="px-4 py-3">{purchase.status}</td>
                      <td className="px-4 py-3 tabular-nums">
                        {purchase.amount_cents != null
                          ? formatCurrency(String(purchase.amount_cents / 100))
                          : "—"}
                      </td>
                      <td className="px-4 py-3 tabular-nums">
                        {formatDeveloperTimestamp(purchase.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </DeveloperDetailSection>
        )}

        {(audit.validation_report || audit.scan_report) && (
          <DeveloperDetailSection title="Raw diagnostics">
            {audit.validation_report && (
              <pre className="overflow-x-auto rounded-xl border border-line/60 bg-secondary/20 p-4 text-xs">
                {JSON.stringify(audit.validation_report, null, 2)}
              </pre>
            )}
            {audit.scan_report && (
              <pre className="overflow-x-auto rounded-xl border border-line/60 bg-secondary/20 p-4 text-xs">
                {JSON.stringify(audit.scan_report, null, 2)}
              </pre>
            )}
          </DeveloperDetailSection>
        )}
      </GlassCard>
    </div>
  );
}
