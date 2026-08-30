import type { Metadata } from "next";

import { EstimatorQuestionnaireClient } from "@/components/estimator/estimator-questionnaire-client";
import { SiteFooter } from "@/components/site-footer";

export const metadata: Metadata = {
  title: "Revenue Leakage Assessment | Paevo",
  robots: { index: false },
};

export default function EstimatorStartPage() {
  return (
    <>
      <EstimatorQuestionnaireClient />
      <SiteFooter variant="minimal" />
    </>
  );
}
