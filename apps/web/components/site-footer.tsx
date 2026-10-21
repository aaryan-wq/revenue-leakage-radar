import Link from "next/link";

import { Logo } from "@/components/brand/logo";
import { cn } from "@/lib/utils";

type SiteFooterProps = {
  variant?: "default" | "minimal";
  className?: string;
};

const columns = [
  {
    title: "Product",
    links: [
      { href: "/how-it-works", label: "How it works" },
      { href: "/saas-revenue-leakage-calculator", label: "Calculator" },
      { href: "/pricing", label: "Pricing" },
      { href: "/security", label: "Security" },
      { href: "/demo", label: "Demo" },
    ],
  },
  {
    title: "Company",
    links: [
      { href: "/faq", label: "FAQ" },
      { href: "/contact", label: "Contact" },
      { href: "/feedback", label: "Feedback" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/terms", label: "Terms" },
      { href: "/privacy", label: "Privacy" },
    ],
  },
] as const;

function FooterLinks({ className }: { className?: string }) {
  return (
    <div className={cn("grid grid-cols-2 gap-8 sm:grid-cols-3", className)}>
      {columns.map((column) => (
        <div key={column.title}>
          <p className="text-sm font-medium text-foreground">{column.title}</p>
          <ul className="mt-3 space-y-2">
            {column.links.map((link) => (
              <li key={link.href}>
                <Link
                  href={link.href}
                  className="text-sm text-muted-foreground transition-colors hover:text-foreground"
                >
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export function SiteFooter({ variant = "default", className }: SiteFooterProps) {
  if (variant === "minimal") {
    return (
      <footer className={cn("border-t border-line bg-field", className)}>
        <div className="mx-auto flex max-w-marketing flex-col gap-4 px-6 py-8 text-sm text-muted-foreground md:flex-row md:items-center md:justify-between md:px-10">
          <span>© {new Date().getFullYear()} Paevo.</span>
          <div className="flex flex-wrap gap-x-6 gap-y-2">
            <Link href="/how-it-works" className="transition-colors hover:text-foreground">
              How it works
            </Link>
            <Link href="/pricing" className="transition-colors hover:text-foreground">
              Pricing
            </Link>
            <Link href="/security" className="transition-colors hover:text-foreground">
              Security
            </Link>
            <Link href="/faq" className="transition-colors hover:text-foreground">
              FAQ
            </Link>
            <Link href="/terms" className="transition-colors hover:text-foreground">
              Terms
            </Link>
            <Link href="/privacy" className="transition-colors hover:text-foreground">
              Privacy
            </Link>
          </div>
        </div>
      </footer>
    );
  }

  return (
    <footer className={cn("border-t border-line bg-field", className)}>
      <div className="mx-auto max-w-marketing px-6 py-12 md:px-10 md:py-16">
        <div className="flex flex-col gap-10 md:flex-row md:items-start md:justify-between">
          <Logo variant="full" href="/" className="h-8" />
          <FooterLinks className="md:max-w-xl md:flex-1" />
        </div>
        <p className="mt-10 text-sm text-muted-foreground">© {new Date().getFullYear()} Paevo.</p>
      </div>
    </footer>
  );
}
