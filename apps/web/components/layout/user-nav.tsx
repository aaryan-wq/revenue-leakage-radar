"use client";

import { SignInButton, SignedIn, SignedOut, UserButton } from "@clerk/nextjs";

import { Button } from "@/components/ui/button";

export function UserNav() {
  return (
    <>
      <SignedOut>
        <SignInButton mode="modal">
          <Button variant="secondary" size="sm">
            Sign In
          </Button>
        </SignInButton>
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </>
  );
}
