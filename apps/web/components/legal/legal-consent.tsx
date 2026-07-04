import Link from "next/link";

import { cn } from "@/lib/utils";

import { LEGAL_ROUTES } from "@/components/legal/legal-links";

type LegalConsentProps = {
  action?: string;
  className?: string;
};

export function LegalConsent({ action = "using Paevo", className }: LegalConsentProps) {
  return (
    <p className={cn("text-xs leading-relaxed text-muted-foreground", className)}>
      By {action}, you agree to our{" "}
      <Link href={LEGAL_ROUTES.terms} className="text-foreground underline-offset-4 hover:underline">
        Terms of Service
      </Link>{" "}
      and{" "}
      <Link href={LEGAL_ROUTES.privacy} className="text-foreground underline-offset-4 hover:underline">
        Privacy Policy
      </Link>
      .
    </p>
  );
}
