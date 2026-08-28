"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { AlertTriangle } from "lucide-react";

import { CheckoutButton } from "@/components/summary/checkout-button";
import { Reveal } from "@/components/motion";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";
import { useAppAuth } from "@/lib/app-auth";
import { isClerkConfigured } from "@/lib/clerk";
import { PRODUCT_NAMES } from "@/lib/pricing-content";

interface DataIntegrityWarningProps {
  reportId: string;
  recoverableArr: string;
  onUnlocked?: () => void;
}

export function DataIntegrityWarning({
  reportId,
  recoverableArr,
  onUnlocked,
}: DataIntegrityWarningProps) {
  const { isSignedIn } = useAppAuth();
  const pathname = usePathname();
  const signInHref = `/sign-in?redirect_url=${encodeURIComponent(pathname)}`;

  return (
    <section className="border-t border-line pt-12">
      <Reveal>
        <HairlineCard padding="lg" className="border-leak/25 bg-leak/10">
          <div className="flex items-start gap-4">
            <AlertTriangle
              className="mt-1 h-6 w-6 shrink-0 text-leak"
              strokeWidth={1.75}
              aria-hidden
            />
            <div className="min-w-0 flex-1">
              <Badge variant="warning">System Warning</Badge>
              <h3 className="mt-4 font-heading text-xl tracking-tight text-foreground">
                Risk Warning for Internal Data Teams
              </h3>
              <div className="mt-4 space-y-3 text-sm leading-relaxed text-muted-foreground">
                <p>
                  Standard SQL or Pandas merges on billing vs. CRM exports produce a{" "}
                  <span className="font-medium text-foreground">~34% false-positive rate</span>{" "}
                  because of mismatched company names, parent-subsidiary billing structures, and
                  currency normalization gaps.
                </p>
                <p>
                  Contacting customers about underpayment based on an unverified internal script
                  creates severe client friction, escalations, and churn risk.
                </p>
                <p>
                  The paid {PRODUCT_NAMES.verificationReport} uses our proprietary
                  entity-resolution engine to deliver{" "}
                  <span className="font-medium text-foreground">100% auditable accuracy</span> with
                  invoice-level evidence you can defend to finance and legal.
                </p>
              </div>
              <div className="mt-6 [&>div]:items-start">
                {!isSignedIn ? (
                  isClerkConfigured() ? (
                    <Link href={signInHref}>
                      <Button size="lg" type="button">
                        Unlock 100% Auditable Report
                      </Button>
                    </Link>
                  ) : (
                    <Button
                      size="lg"
                      disabled
                      title="Add NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY to .env to enable sign-in"
                    >
                      Unlock 100% Auditable Report
                    </Button>
                  )
                ) : (
                  <CheckoutButton
                    plan="single_report"
                    reportId={reportId}
                    recoverableArr={recoverableArr}
                    label="Unlock 100% Auditable Report"
                    analyticsSource="data_integrity_warning"
                    onCreditUnlock={onUnlocked}
                  />
                )}
              </div>
            </div>
          </div>
        </HairlineCard>
      </Reveal>
    </section>
  );
}
