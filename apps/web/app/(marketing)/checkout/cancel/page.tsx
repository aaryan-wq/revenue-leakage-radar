import Link from "next/link";

import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";

interface CheckoutCancelPageProps {
  searchParams: Promise<{ report_id?: string }>;
}

export default async function CheckoutCancelPage({ searchParams }: CheckoutCancelPageProps) {
  const params = await searchParams;
  const reportId = params.report_id;

  return (
    <div className="mx-auto max-w-reading px-8 py-24">
      <Reveal>
        <HairlineCard padding="lg" className="text-center">
          <p className="text-[0.78rem] uppercase tracking-[0.18em] text-muted-foreground">Checkout</p>
          <h1 className="mt-4 font-heading text-[clamp(2rem,4vw,2.75rem)] leading-[1.05] tracking-tight">
            Checkout Cancelled
          </h1>
          <p className="mt-4 text-muted-foreground">
            Your payment was not completed. Your free audit summary is still available.
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
        </HairlineCard>
      </Reveal>
    </div>
  );
}
