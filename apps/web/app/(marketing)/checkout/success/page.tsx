import { Suspense } from "react";

import { CheckoutSuccessClient } from "@/components/checkout/checkout-success-client";

export default function CheckoutSuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-reading px-6 py-24 text-center text-muted-foreground md:px-10">
          Loading…
        </div>
      }
    >
      <CheckoutSuccessClient />
    </Suspense>
  );
}
