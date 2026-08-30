import type { Metadata } from "next";
import { Suspense } from "react";

import { EstimatorQuestionnaireClient } from "@/components/estimator/estimator-questionnaire-client";
import { SiteFooter } from "@/components/site-footer";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";

export const metadata: Metadata = {
  title: "Revenue Leakage Assessment | Paevo",
  robots: { index: false },
};

export default function EstimatorStartPage() {
  return (
    <>
      <Suspense fallback={<PageLoadingSkeleton message="Preparing your assessment…" />}>
        <EstimatorQuestionnaireClient />
      </Suspense>
      <SiteFooter variant="minimal" />
    </>
  );
}
