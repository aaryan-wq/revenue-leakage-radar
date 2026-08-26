import type { Metadata } from "next";

import { DemoFindingPageClient } from "@/components/demo/demo-finding-page-client";

export const metadata: Metadata = {
  title: "Sample Finding",
  description: "Detailed evidence and remediation for a sample revenue leakage finding.",
};

interface DemoFindingPageProps {
  params: Promise<{ slug: string }>;
}

export default async function DemoFindingPage({ params }: DemoFindingPageProps) {
  const { slug } = await params;
  return <DemoFindingPageClient slug={slug} />;
}
