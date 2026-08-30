import type { Metadata } from "next";

import { EstimatorLandingClient } from "@/components/estimator/estimator-landing-client";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "SaaS Revenue Leakage Calculator | Paevo",
  description:
    "Free modeled revenue leakage estimate for SaaS billing environments. No billing data required.",
};

export default function EstimatorLandingPage() {
  return (
    <>
      <EstimatorLandingClient />
      <SiteFooter />
    </>
  );
}
