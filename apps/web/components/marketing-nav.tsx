"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

import { Logo, NAV_LOGO_CLASS, NAV_ROW_CLASS } from "@/components/brand/logo";
import { MarketingAuthActions } from "@/components/marketing-auth-actions";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Overview" },
  { href: "/how-it-works", label: "How It Works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/security", label: "Security" },
  { href: "/faq", label: "FAQ" },
];

function isLinkActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function MarketingNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50">
      <div className="absolute inset-0 -z-10 bg-background/70 backdrop-blur-xl" />
      <nav
        className={cn(
          "relative mx-auto max-w-marketing justify-between gap-4 px-6 md:px-10",
          NAV_ROW_CLASS,
        )}
      >
        <Logo variant="full" priority className={cn("hidden sm:block", NAV_LOGO_CLASS.full)} />
        <Logo variant="short" priority className={cn("sm:hidden", NAV_LOGO_CLASS.short)} />

        <div className="pointer-events-none absolute left-1/2 top-5 hidden -translate-x-1/2 md:block">
          <div className="pointer-events-auto flex items-start gap-0.5">
            {links.map((link) => {
              const active = isLinkActive(pathname, link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className="relative px-3.5 py-2 text-[0.8rem] tracking-wide text-muted-foreground transition-colors hover:text-foreground"
                >
                  {active && (
                    <motion.span
                      layoutId="marketing-nav-pill"
                      className="absolute inset-0 rounded-full bg-secondary"
                      transition={{ type: "spring", stiffness: 380, damping: 32 }}
                    />
                  )}
                  <span className={active ? "relative text-foreground" : "relative"}>
                    {link.label}
                  </span>
                </Link>
              );
            })}
          </div>
        </div>

        <MarketingAuthActions className="items-start" />
      </nav>
    </header>
  );
}
