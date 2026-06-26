import { Suspense } from "react";

import { CheckoutSuccessClient } from "@/components/checkout/checkout-success-client";

export default function CheckoutSuccessPage() {
  return (
    <Suspense
      fallback={
        <div className="mx-auto max-w-reading px-8 py-24 text-center text-body text-gray-500">
          Loading…
        </div>
      }
    >
      <CheckoutSuccessClient />
    </Suspense>
  );
}
