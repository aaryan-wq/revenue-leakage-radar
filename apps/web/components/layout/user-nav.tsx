"use client";

import { SignedIn, SignedOut, SignInButton, SignUpButton, UserButton } from "@clerk/nextjs";

export function UserNav() {
  return (
    <>
      <SignedOut>
        <div className="flex items-center gap-2">
          <SignInButton mode="redirect">
            <span className="glass-subtle inline-flex h-10 cursor-pointer items-center justify-center rounded-button border border-border px-4 text-small font-medium text-primary transition-all hover:border-border-strong">
              Sign In
            </span>
          </SignInButton>
          <SignUpButton mode="redirect">
            <span className="inline-flex h-10 cursor-pointer items-center justify-center rounded-button bg-primary px-4 text-small font-medium text-white transition-all hover:brightness-[1.04] active:scale-[0.98]">
              Sign Up
            </span>
          </SignUpButton>
        </div>
      </SignedOut>
      <SignedIn>
        <UserButton afterSignOutUrl="/" />
      </SignedIn>
    </>
  );
}
