import type {
  FindingDetailResponse,
  FindingResponse,
  ReportDetailResponse,
} from "@rlr/shared";

import rawFixture from "./acmecrm-demo.fixture.json";

type DemoFixture = {
  report: ReportDetailResponse;
  findings: FindingResponse[];
  finding_details: Record<string, FindingDetailResponse>;
  slugs: Record<string, string>;
};

const fixture = rawFixture as DemoFixture;

const findingIdToSlug = new Map<string, string>(
  Object.entries(fixture.slugs).map(([slug, id]) => [id, slug]),
);

export function getDemoReport(): ReportDetailResponse {
  return fixture.report;
}

export function getDemoFindings(): FindingResponse[] {
  return fixture.findings;
}

export function getDemoFindingBySlug(slug: string): FindingDetailResponse | null {
  return fixture.finding_details[slug] ?? null;
}

export function getDemoFindingSlug(finding: FindingResponse): string | null {
  return findingIdToSlug.get(finding.id) ?? null;
}

export function getDemoFindingHref(finding: FindingResponse): string {
  const slug = getDemoFindingSlug(finding);
  return slug ? `/demo/findings/${slug}` : "/demo";
}

export const DEMO_FINDING_SLUGS = Object.keys(fixture.finding_details);
