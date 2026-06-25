import Link from "next/link";
import { Radar } from "lucide-react";

import { Button } from "@/components/ui/button";
import { isClerkConfigured } from "@/lib/clerk";
import { UserNav } from "./user-nav";

export function TopNav() {
  return (
    <header className="sticky top-0 z-50 h-[72px] border-b border-gray-100 bg-white">
      <div className="mx-auto flex h-full max-w-container items-center justify-between px-8">
        <Link href="/" className="flex items-center gap-3 text-primary">
          <Radar className="h-6 w-6" strokeWidth={1.75} />
          <span className="text-h4 font-semibold tracking-tight">Revenue Leakage Radar</span>
        </Link>

        <nav className="flex items-center gap-6">
          <Link href="/pricing" className="text-small text-gray-500 hover:text-gray-900 transition-colors">
            Pricing
          </Link>
          <Link href="/security" className="text-small text-gray-500 hover:text-gray-900 transition-colors">
            Security
          </Link>
          {isClerkConfigured() ? (
            <UserNav />
          ) : (
            <Button variant="secondary" size="sm" disabled>
              Sign In
            </Button>
          )}
          <Link
            href="/upload"
            className="inline-flex h-10 items-center justify-center rounded-button bg-primary px-4 text-small font-medium text-white transition-all duration-fast hover:brightness-[1.02]"
          >
            Run Free Scan
          </Link>
        </nav>
      </div>
    </header>
  );
}
