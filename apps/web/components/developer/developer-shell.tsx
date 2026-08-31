"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

import { Button } from "@/components/ui/button";
import { PageLoadingSkeleton } from "@/components/ui/page-loading";
import { useAdminAccess } from "@/lib/hooks/use-admin-access";
import { cn } from "@/lib/utils";

const tabs = [
  { href: "/developer", label: "Overview", exact: true },
  { href: "/developer/audits", label: "Audits", exact: false },
  { href: "/developer/reports", label: "Reports", exact: false },
  { href: "/developer/logs", label: "Logs", exact: false },
  { href: "/developer/notes", label: "Notes", exact: false },
] as const;

function isTabActive(pathname: string, href: string, exact: boolean): boolean {
  if (exact) return pathname === href;
  return pathname.startsWith(href);
}

export function DeveloperShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { isAdmin, isChecking, accessDenied, reload } = useAdminAccess();

  if (isChecking) {
    return <PageLoadingSkeleton message="Verifying developer access…" variant="dashboard" />;
  }

  if (accessDenied || !isAdmin) {
    return (
      <div className="mx-auto max-w-report px-6 py-24 text-center md:px-10">
        <h1 className="font-heading text-2xl tracking-tight">Access restricted</h1>
        <p className="mt-3 text-muted-foreground">
          This workspace is limited to authorized developer accounts.
        </p>
        <Link
          href="/dashboard"
          className="mt-8 inline-flex h-11 items-center rounded-full bg-primary px-6 text-[0.92rem] font-medium text-primary-foreground"
        >
          Back to dashboard
        </Link>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-marketing px-6 pb-20 pt-10 md:px-10">
      <div className="mb-8 flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
        <div>
          <p className="text-overline text-muted-foreground">Internal</p>
          <h1 className="mt-2 font-heading text-3xl tracking-tight">Developer dashboard</h1>
          <p className="mt-2 max-w-readable text-muted-foreground">
            Platform operations, audit oversight, and support tooling.
          </p>
        </div>
        <Button variant="secondary" size="sm" onClick={() => void reload()}>
          Refresh access
        </Button>
      </div>

      <nav className="mb-8 flex flex-wrap gap-1 border-b border-line/60 pb-3">
        {tabs.map((tab) => {
          const active = isTabActive(pathname, tab.href, tab.exact);
          return (
            <Link
              key={tab.href}
              href={tab.href}
              className={cn(
                "relative rounded-full px-4 py-2 text-sm transition-colors",
                active ? "text-foreground" : "text-muted-foreground hover:text-foreground",
              )}
            >
              {active && (
                <motion.span
                  layoutId="developer-tab-pill"
                  className="absolute inset-0 rounded-full bg-secondary"
                  transition={{ type: "spring", stiffness: 380, damping: 32 }}
                />
              )}
              <span className="relative">{tab.label}</span>
            </Link>
          );
        })}
      </nav>

      {children}
    </div>
  );
}
