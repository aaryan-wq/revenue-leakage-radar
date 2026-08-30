import type { Metadata } from "next";

import { EstimatorShareClient } from "@/components/estimator/estimator-share-client";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Shared Leakage Estimate | Paevo",
  robots: { index: false },
};

export default async function EstimatorSharePage({ params }: { params: Promise<{ token: string }> }) {
  const { token } = await params;
  return (
    <>
      <EstimatorShareClient token={token} />
      <SiteFooter />
    </>
  );
}
