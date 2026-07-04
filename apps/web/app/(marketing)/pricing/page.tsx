import { Suspense } from "react";

import { PricingPageClient } from "@/components/pricing/pricing-page-client";
import { SiteFooter } from "@/components/marketing/site-footer";

export default function PricingPage() {
  return (
    <>
      <Suspense
        fallback={
          <div className="mx-auto max-w-reading px-6 py-24 text-center text-muted-foreground md:px-10">
            Loading pricing…
          </div>
        }
      >
        <PricingPageClient />
      </Suspense>
      <SiteFooter />
    </>
  );
}
