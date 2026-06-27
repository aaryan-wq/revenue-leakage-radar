"use client";

import Link from "next/link";
import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

import { Button } from "@/components/ui/button";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { isClerkConfigured } from "@/lib/clerk";

export function MarketingAuthActions() {
  if (!isClerkConfigured()) {
    return (
      <Link href="/sign-in">
        <Button variant="ghost" size="sm">
          Sign In
        </Button>
      </Link>
    );
  }

  return (
    <>
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
    </>
  );
}
