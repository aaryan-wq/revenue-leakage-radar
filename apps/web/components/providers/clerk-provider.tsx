"use client";

import { ClerkProvider } from "@clerk/nextjs";
import type { ReactNode } from "react";

import { AppAuthProvider } from "@/lib/app-auth";
import { clerkAppearance } from "@/lib/clerk-appearance";
import { isClerkConfigured } from "@/lib/clerk";

export function ClerkProviderWrapper({ children }: { children: ReactNode }) {
  if (!isClerkConfigured()) {
    if (process.env.NODE_ENV === "production") {
      throw new Error(
        "NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY must be set in production.",
      );
    }
    return <AppAuthProvider>{children}</AppAuthProvider>;
  }

  return (
    <ClerkProvider
      appearance={clerkAppearance}
      signInFallbackRedirectUrl="/dashboard"
      signUpFallbackRedirectUrl="/dashboard"
    >
      <AppAuthProvider>{children}</AppAuthProvider>
    </ClerkProvider>
  );
}
