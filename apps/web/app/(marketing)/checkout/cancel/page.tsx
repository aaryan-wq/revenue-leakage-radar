import Link from "next/link";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";

interface CheckoutCancelPageProps {
  searchParams: Promise<{ report_id?: string }>;
}

export default async function CheckoutCancelPage({ searchParams }: CheckoutCancelPageProps) {
  const params = await searchParams;
  const reportId = params.report_id;

  return (
    <div className="mx-auto max-w-reading px-8 py-24">
      <GlassCard padding="lg" elevated className="text-center">
        <p className="text-overline uppercase text-gray-500">Checkout</p>
        <h1 className="mt-4 text-h1 text-primary">Checkout Cancelled</h1>
        <p className="mt-4 text-body text-gray-600">
          Your payment was not completed. Your free summary is still available.
        </p>
        <div className="mt-10 flex flex-wrap justify-center gap-4">
          <Link href="/summary">
            <Button size="lg">Back to Summary</Button>
          </Link>
          {reportId && (
            <Link href={`/pricing?report_id=${reportId}`}>
              <Button variant="secondary" size="lg">
                View Pricing
              </Button>
            </Link>
          )}
        </div>
      </GlassCard>
    </div>
  );
}
