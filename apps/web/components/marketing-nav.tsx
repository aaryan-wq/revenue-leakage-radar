"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { Menu, X } from "lucide-react";

import { Logo, NAV_LOGO_CLASS } from "@/components/brand/logo";
import { MarketingAuthActions } from "@/components/marketing-auth-actions";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { ViewSampleReportCta } from "@/components/marketing/view-sample-report-cta";
import { cn } from "@/lib/utils";

const links = [
  { href: "/how-it-works", label: "How it works" },
  { href: "/saas-revenue-leakage-calculator", label: "Calculator" },
  { href: "/pricing", label: "Pricing" },
  { href: "/security", label: "Security" },
];

function isLinkActive(pathname: string, href: string): boolean {
  return pathname.startsWith(href);
}

export function MarketingNav() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!menuOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [menuOpen]);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 1024px)");
    const onChange = () => {
      if (media.matches) setMenuOpen(false);
    };
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-background">
      <nav className="mx-auto flex h-16 max-w-marketing items-center gap-6 px-6 md:px-10">
        <Logo variant="full" priority className={cn("hidden shrink-0 sm:block", NAV_LOGO_CLASS.full)} />
        <Logo variant="short" priority className={cn("shrink-0 sm:hidden", NAV_LOGO_CLASS.short)} />

        <div className="hidden items-center gap-1 lg:flex">
          {links.map((link) => {
            const active = isLinkActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "px-3 py-2 text-sm transition-colors",
                  active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
                )}
              >
                {link.label}
              </Link>
            );
          })}
        </div>

        <div className="ml-auto flex shrink-0 items-center gap-2">
          <ViewSampleReportCta
            size="sm"
            label="Sample report"
            analyticsSource="marketing_nav"
            className="hidden lg:inline-flex"
          />
          <RunFreeAuditCta
            size="sm"
            showArrow={false}
            label="Free scan"
            analyticsSource="marketing_nav"
            className="hidden lg:inline-flex"
          />
          <MarketingAuthActions className="shrink-0 items-center" />
          <button
            type="button"
            className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-foreground transition-colors hover:bg-secondary lg:hidden"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            aria-controls={menuId}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? <X className="h-5 w-5" strokeWidth={1.75} /> : <Menu className="h-5 w-5" strokeWidth={1.75} />}
          </button>
        </div>
      </nav>

      {menuOpen ? (
        <div id={menuId} className="border-t border-line bg-background lg:hidden">
          <div className="flex flex-col gap-2 px-4 pt-3">
            <RunFreeAuditCta
              size="md"
              showArrow={false}
              label="Free scan"
              analyticsSource="marketing_nav"
            />
            <ViewSampleReportCta size="md" label="Sample report" analyticsSource="marketing_nav" />
          </div>
          <ul className="px-4 py-3">
            {links.map((link) => {
              const active = isLinkActive(pathname, link.href);
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    onClick={() => setMenuOpen(false)}
                    className={cn(
                      "flex min-h-11 items-center rounded-lg px-3 text-sm",
                      active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
                    )}
                  >
                    {link.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ) : null}
    </header>
  );
}
