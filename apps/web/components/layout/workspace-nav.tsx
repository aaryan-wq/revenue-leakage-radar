"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { UserButton } from "@clerk/nextjs";
import { Radar } from "lucide-react";

import { isClerkConfigured } from "@/lib/clerk";
import { cn } from "@/lib/utils";

const WORKSPACE_LINKS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/billing", label: "Billing" },
  { href: "/account", label: "Account" },
];

export function WorkspaceNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-sticky h-[72px] glass-elevated border-b border-border">
      <div className="mx-auto flex h-full max-w-container items-center justify-between px-8">
        <Link
          href="/dashboard"
          className="flex items-center gap-3 text-primary transition-opacity hover:opacity-80"
        >
          <Radar className="h-6 w-6" strokeWidth={1.75} />
          <span className="text-h4 font-semibold tracking-tight">Revenue Leakage Radar</span>
        </Link>

        <nav className="flex items-center gap-6">
          {WORKSPACE_LINKS.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={cn(
                "relative text-small transition-colors",
                pathname === link.href ? "font-medium text-gray-900" : "text-gray-500 hover:text-gray-900",
              )}
            >
              {link.label}
              {pathname === link.href && (
                <span className="absolute -bottom-[1.35rem] left-0 right-0 h-0.5 rounded-full bg-primary" />
              )}
            </Link>
          ))}
          {isClerkConfigured() ? (
            <UserButton afterSignOutUrl="/" />
          ) : (
            <span
              className="inline-flex h-10 items-center rounded-button border border-border px-4 text-small text-gray-400"
              title="Configure Clerk to enable sign in"
            >
              Account
            </span>
          )}
          <Link
            href="/upload"
            className="glass-subtle inline-flex h-10 items-center justify-center rounded-button border border-border px-4 text-small font-medium text-primary transition-all hover:border-border-strong active:scale-[0.98]"
          >
            New Scan
          </Link>
        </nav>
      </div>
    </header>
  );
}
