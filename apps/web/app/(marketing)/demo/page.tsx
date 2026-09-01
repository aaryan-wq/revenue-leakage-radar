import type { Metadata } from "next";

import { DemoReportPageClient } from "@/components/demo/demo-report-page-client";

export const metadata: Metadata = {
  title: "Sample Report",
  description:
    "Explore a sample Revenue Verification Report for Meridian Platform, a $27M ARR B2B SaaS company, with full findings, evidence, and recoverable ARR.",
};

export default function DemoPage() {
  return <DemoReportPageClient />;
}
