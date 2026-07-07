"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton, useUser } from "@clerk/nextjs";
import { motion } from "framer-motion";

import { Logo, NAV_GREETING_CLASS, NAV_LOGO_CLASS, NAV_ROW_CLASS } from "@/components/brand/logo";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { formatGreeting } from "@/lib/greeting";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { isClerkConfigured } from "@/lib/clerk";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Home", prefetch: true },
  { href: "/audits", label: "Audits", prefetch: true },
  { href: "/billing", label: "Billing", prefetch: false },
  { href: "/integrations", label: "Integrations", prefetch: false },
  { href: "/team", label: "Team", prefetch: false },
  { href: "/account", label: "Settings", prefetch: false },
  { href: "/help", label: "Help", prefetch: false },
  { href: "/feedback", label: "Feedback", prefetch: false },
] as const;

function isLinkActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") {
    return pathname === "/dashboard" || pathname === "/workspace";
  }
  if (href === "/audits") {
    return (
      pathname.startsWith("/audits") ||
      pathname.startsWith("/report/") ||
      pathname.startsWith("/findings/")
    );
  }
  return pathname.startsWith(href);
}

function WorkspaceGreeting() {
  const { user, isLoaded } = useUser();

  if (!isLoaded) {
    return <div className="hidden h-9 w-48 animate-pulse rounded bg-secondary lg:block" aria-hidden="true" />;
  }

  const name = user?.firstName || user?.fullName || "there";
  return <p className={NAV_GREETING_CLASS}>{formatGreeting(name)}</p>;
}

export function WorkspaceNav() {
  const pathname = usePathname();
  const clerkReady = isClerkConfigured();

  return (
    <header className="sticky top-0 z-50 border-b border-line/60">
      <div className="absolute inset-0 -z-10 bg-background/85 backdrop-blur-xl" />
      <nav className="mx-auto max-w-marketing px-6 md:px-10">
        <div className={cn("justify-between gap-4", NAV_ROW_CLASS)}>
          <div className="flex min-w-0 items-start gap-4">
            <Logo variant="short" href="/dashboard" className={NAV_LOGO_CLASS.short} />
            {clerkReady ? (
              <WorkspaceGreeting />
            ) : (
              <p className={NAV_GREETING_CLASS}>{formatGreeting("there")}</p>
            )}
          </div>

          <div className="flex shrink-0 items-start gap-2 sm:gap-3">
            <RunFreeAuditCta
              size="sm"
              fromWorkspace
              className="hidden h-9 items-center md:inline-flex"
            />
            {clerkReady ? (
              <UserButton appearance={clerkAppearance} />
            ) : (
              <Link
                href="/sign-in"
                className="inline-flex h-9 items-center rounded-full bg-primary px-4 text-[0.8rem] font-medium text-primary-foreground"
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
                prefetch={link.prefetch}
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
