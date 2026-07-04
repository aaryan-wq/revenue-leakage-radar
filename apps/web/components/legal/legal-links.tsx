import Link from "next/link";

import { cn } from "@/lib/utils";

export const LEGAL_ROUTES = {
  terms: "/terms",
  privacy: "/privacy",
} as const;

type LegalLinksProps = {
  className?: string;
  linkClassName?: string;
};

export function LegalLinks({ className, linkClassName }: LegalLinksProps) {
  const linkStyles = cn(
    "text-muted-foreground transition-colors hover:text-foreground",
    linkClassName,
  );

  return (
    <nav
      className={cn("flex flex-wrap items-center gap-x-4 gap-y-1", className)}
      aria-label="Legal"
    >
      <Link href={LEGAL_ROUTES.terms} className={linkStyles}>
        Terms of Service
      </Link>
      <Link href={LEGAL_ROUTES.privacy} className={linkStyles}>
        Privacy Policy
      </Link>
    </nav>
  );
}
