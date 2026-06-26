"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { SignedIn } from "@clerk/nextjs";
import { Radar } from "lucide-react";

import { isClerkConfigured } from "@/lib/clerk";
import { cn } from "@/lib/utils";
import { UserNav } from "./user-nav";

const NAV_LINKS = [
  { href: "/pricing", label: "Pricing" },
  { href: "/security", label: "Security" },
];

export function MarketingNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-sticky h-[72px] glass-elevated border-b border-border">
      <div className="mx-auto flex h-full max-w-container items-center justify-between px-8">
        <Link href="/" className="flex items-center gap-3 text-primary transition-opacity hover:opacity-80">
          <Radar className="h-6 w-6" strokeWidth={1.75} />
          <span className="text-h4 font-semibold tracking-tight">Revenue Leakage Radar</span>
        </Link>

        <nav className="flex items-center gap-6">
          {NAV_LINKS.map((link) => (
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
          {isClerkConfigured() && (
            <SignedIn>
              <Link
                href="/dashboard"
                className={cn(
                  "text-small transition-colors",
                  pathname.startsWith("/dashboard")
                    ? "font-medium text-gray-900"
                    : "text-gray-500 hover:text-gray-900",
                )}
              >
                Dashboard
              </Link>
            </SignedIn>
          )}
          {isClerkConfigured() ? (
            <UserNav />
          ) : (
            <span
              className="inline-flex h-10 items-center rounded-button border border-border px-4 text-small text-gray-400"
              title="Configure Clerk to enable sign in"
            >
              Sign In
            </span>
          )}
          <Link
            href="/upload"
            className="inline-flex h-10 items-center justify-center rounded-button bg-primary px-4 text-small font-medium text-white transition-all duration-fast hover:brightness-[1.04] active:scale-[0.98]"
          >
            Run Free Scan
          </Link>
        </nav>
      </div>
    </header>
  );
}
