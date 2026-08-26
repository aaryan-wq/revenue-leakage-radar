"use client";

import Link from "next/link";

import { DemoBanner } from "@/components/demo/demo-banner";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { Reveal } from "@/components/motion";
import { ReportView } from "@/components/report/report-view";
import { useTrackOnce } from "@/lib/analytics/hooks";
import {
  getDemoFindingHref,
  getDemoFindings,
  getDemoReport,
} from "@/lib/demo/demo-fixture";
import { AnalyticsEvents } from "@rlr/shared";

export function DemoReportPageClient() {
  const report = getDemoReport();
  const findings = getDemoFindings();

  useTrackOnce(AnalyticsEvents.DEMO_REPORT_VIEWED, { company_name: report.company_name ?? "AcmeCRM" });

  return (
    <>
      <DemoBanner />
      <ReportView
        report={report}
        mode="demo"
        findings={findings}
        getFindingHref={getDemoFindingHref}
        footer={
          <Reveal>
            <div className="mt-12 flex flex-col items-start justify-between gap-6 border-t border-line pt-10 md:flex-row md:items-center">
              <div className="max-w-md">
                <p className="font-heading text-xl tracking-tight text-foreground">
                  Ready to see your own numbers?
                </p>
                <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                  Upload billing exports and receive a free audit summary in minutes. Unlock the
                  full verification report when the recoverable revenue justifies it.
                </p>
              </div>
              <RunFreeAuditCta analyticsSource="demo_report_footer" />
            </div>
            <div className="mt-8">
              <Link
                href="/"
                className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
              >
                ← Back to home
              </Link>
            </div>
          </Reveal>
        }
      />
    </>
  );
}
