"use client";

import Link from "next/link";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

import { cn } from "@/lib/utils";

import { Button } from "@/components/ui/button";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { isClerkConfigured } from "@/lib/clerk";

export function MarketingAuthActions({ className }: { className?: string }) {
  if (!isClerkConfigured()) {
    return (
      <Link href="/sign-in" className={cn("inline-flex items-start gap-2", className)}>
        <Button variant="ghost" size="sm">
          Sign In
        </Button>
      </Link>
    );
  }

  return (
    <div className={cn("flex items-start gap-2", className)}>
      <SignedOut>
        <SignInButton mode="modal" forceRedirectUrl="/dashboard">
          <Button variant="ghost" size="sm">
            Sign In
          </Button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <Link href="/dashboard">
          <Button variant="ghost" size="sm">
            Workspace
          </Button>
        </Link>
        <UserButton appearance={clerkAppearance} />
      </SignedIn>
    </div>
  );
}
