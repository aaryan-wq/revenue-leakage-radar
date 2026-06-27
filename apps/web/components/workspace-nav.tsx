"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton, useUser } from "@clerk/nextjs";
import { motion } from "framer-motion";

import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { formatGreeting } from "@/lib/greeting";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { isClerkConfigured } from "@/lib/clerk";

const links = [
  { href: "/dashboard", label: "Home" },
  { href: "/audits", label: "Audits" },
  { href: "/reports", label: "Reports" },
  { href: "/uploads", label: "Uploads" },
  { href: "/billing", label: "Billing" },
  { href: "/integrations", label: "Integrations" },
  { href: "/team", label: "Team" },
  { href: "/account", label: "Settings" },
  { href: "/help", label: "Help" },
];

function isLinkActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") {
    return pathname === "/dashboard" || pathname === "/workspace";
  }
  if (href === "/reports") {
    return (
      pathname.startsWith("/reports") ||
      pathname.startsWith("/report/") ||
      pathname.startsWith("/findings/")
    );
  }
  return pathname.startsWith(href);
}

function WorkspaceGreeting() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return <div className="h-5 w-36 animate-pulse rounded bg-secondary" aria-hidden="true" />;
  }

  const name = user?.firstName || user?.fullName || "there";
  return (
    <p className="hidden shrink-0 font-heading text-[0.9rem] tracking-tight text-foreground lg:block">
      {formatGreeting(name)}
    </p>
  );
}

export function WorkspaceNav() {
  const pathname = usePathname();
  const clerkReady = isClerkConfigured();

  return (
    <header className="sticky top-0 z-50 border-b border-line/60">
      <div className="absolute inset-0 -z-10 bg-background/85 backdrop-blur-xl" />
      <nav className="mx-auto max-w-marketing px-6 md:px-10">
        <div className="flex h-[72px] items-center justify-between gap-4">
          {clerkReady ? <WorkspaceGreeting /> : (
            <p className="hidden shrink-0 font-heading text-[0.9rem] tracking-tight lg:block">
              {formatGreeting("there")}
            </p>
          )}

          <div className="flex shrink-0 items-center gap-2 sm:gap-3">
            <RunFreeAuditCta size="sm" className="hidden md:inline-flex" />
            {clerkReady ? (
              <UserButton appearance={clerkAppearance} />
            ) : (
              <Link
                href="/sign-in"
                className="rounded-full bg-primary px-4 py-2 text-[0.8rem] font-medium text-primary-foreground"
              >
                Sign In
              </Link>
            )}
          </div>
        </div>

        <div className="-mx-2 mb-3 flex items-center gap-0.5 overflow-x-auto pb-2 scrollbar-none">
          {links.map((link) => {
            const active = isLinkActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className="relative shrink-0 px-3 py-2 text-[0.78rem] tracking-wide text-muted-foreground transition-colors hover:text-foreground"
              >
                {active && (
                  <motion.span
                    layoutId="workspace-nav-pill"
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
      </nav>
    </header>
  );
}
