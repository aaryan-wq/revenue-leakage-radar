import type { Metadata } from "next";

import { EstimatorMethodologyClient } from "@/components/estimator/estimator-methodology-client";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Calculator Methodology | Paevo",
  description: "How Paevo models SaaS revenue leakage exposure without billing data.",
};

export default function EstimatorMethodologyPage() {
  return (
    <>
      <EstimatorMethodologyClient />
      <SiteFooter variant="minimal" />
    </>
  );
}
