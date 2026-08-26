"use client";

import Link from "next/link";

import { DemoBanner } from "@/components/demo/demo-banner";
import { FindingDetailView } from "@/components/findings/finding-detail-view";
import { useTrackOnce } from "@/lib/analytics/hooks";
import { getDemoFindingBySlug } from "@/lib/demo/demo-fixture";
import { AnalyticsEvents } from "@rlr/shared";

interface DemoFindingPageClientProps {
  slug: string;
}

export function DemoFindingPageClient({ slug }: DemoFindingPageClientProps) {
  const finding = getDemoFindingBySlug(slug);

  useTrackOnce(
    AnalyticsEvents.DEMO_FINDING_VIEWED,
    finding
      ? {
          finding_slug: slug,
          rule_id: finding.rule_id,
        }
      : undefined,
    Boolean(finding),
  );

  if (!finding) {
    return (
      <div className="mx-auto max-w-report px-6 py-20 text-center md:px-10">
        <p className="text-lg text-muted-foreground">Sample finding not found.</p>
        <Link
          href="/demo"
          className="mt-6 inline-block text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
        >
          ← Back to sample report
        </Link>
      </div>
    );
  }

  return (
    <>
      <DemoBanner />
      <FindingDetailView
        finding={finding}
        mode="demo"
        reportHref="/demo"
        backLabel="Back to sample report"
        footer={
          <div className="mt-10 flex flex-wrap gap-4">
            <Link
              href="/demo"
              className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
            >
              ← Back to sample report
            </Link>
            <Link
              href="/upload"
              className="text-sm text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
            >
              Run your own audit
            </Link>
          </div>
        }
      />
    </>
  );
}
