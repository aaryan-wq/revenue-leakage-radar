"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton, useUser } from "@clerk/nextjs";

import { Logo, NAV_GREETING_CLASS, NAV_LOGO_CLASS } from "@/components/brand/logo";
import { RunFreeAuditCta } from "@/components/marketing/run-free-audit-cta";
import { isAdminUser } from "@/lib/admin-access";
import { formatGreeting } from "@/lib/greeting";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { isClerkConfigured } from "@/lib/clerk";
import { cn } from "@/lib/utils";

const baseLinks = [
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
  if (href === "/developer") {
    return pathname.startsWith("/developer");
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
  const { user, isLoaded } = useUser();
  const links = isLoaded && isAdminUser(user)
    ? [
        ...baseLinks.slice(0, 2),
        { href: "/developer", label: "Developer", prefetch: false as const },
        ...baseLinks.slice(2),
      ]
    : [...baseLinks];

  return (
    <header className="sticky top-0 z-50 border-b border-line bg-background">
      <nav className="mx-auto flex h-16 max-w-marketing items-center gap-4 px-6 md:gap-6 md:px-10">
        <Logo variant="short" href="/dashboard" className={NAV_LOGO_CLASS.short} />

        <div className="flex min-w-0 flex-1 items-center gap-1 overflow-x-auto scrollbar-none">
          {links.map((link) => {
            const active = isLinkActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                prefetch={link.prefetch}
                className={cn(
                  "group relative shrink-0 px-3 py-2 text-sm transition-colors duration-fast",
                  active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
                )}
              >
                {link.label}
                <span
                  className={cn(
                    "absolute bottom-1 left-3 h-px bg-current transition-[width] duration-fast ease-glide",
                    active ? "w-[calc(100%-1.5rem)]" : "w-0 group-hover:w-[calc(100%-1.5rem)]",
                  )}
                />
              </Link>
            );
          })}
        </div>

        <div className="flex shrink-0 items-center gap-3">
          {clerkReady ? <WorkspaceGreeting /> : <p className={NAV_GREETING_CLASS}>{formatGreeting("there")}</p>}
          <RunFreeAuditCta size="sm" fromWorkspace className="hidden md:inline-flex" />
          {clerkReady ? (
            <UserButton appearance={clerkAppearance} />
          ) : (
            <Link
              href="/sign-in"
              className="inline-flex h-8 items-center rounded-lg bg-primary px-3 text-sm font-medium text-primary-foreground transition-[filter,transform] duration-fast ease-glide hover:brightness-110 active:scale-[0.98] motion-reduce:transform-none"
            >
              Sign In
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
