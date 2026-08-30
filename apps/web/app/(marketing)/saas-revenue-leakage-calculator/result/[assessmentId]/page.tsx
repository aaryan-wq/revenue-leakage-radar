import type { Metadata } from "next";

import { EstimatorResultClient } from "@/components/estimator/estimator-result-client";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Your Leakage Estimate | Paevo",
  robots: { index: false },
};

export default async function EstimatorResultPage({
  params,
}: {
  params: Promise<{ assessmentId: string }>;
}) {
  const { assessmentId } = await params;
  return (
    <>
      <EstimatorResultClient assessmentId={assessmentId} />
      <SiteFooter />
    </>
  );
}
