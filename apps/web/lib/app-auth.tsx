"use client";

import { useAuth as useClerkAuth } from "@clerk/nextjs";
import { createContext, useContext, type ReactNode } from "react";

import { isClerkConfigured } from "@/lib/clerk";

export interface AppAuthState {
  isLoaded: boolean;
  isSignedIn: boolean;
  getToken: () => Promise<string | null>;
}

const unauthenticatedState: AppAuthState = {
  isLoaded: true,
  isSignedIn: false,
  getToken: async () => null,
};

const AppAuthContext = createContext<AppAuthState>(unauthenticatedState);

function ClerkAuthBridge({ children }: { children: ReactNode }) {
  const { isLoaded, isSignedIn, getToken } = useClerkAuth();
  const value: AppAuthState = {
    isLoaded,
    isSignedIn: isSignedIn ?? false,
    getToken: async () => getToken(),
  };
  return <AppAuthContext.Provider value={value}>{children}</AppAuthContext.Provider>;
}

export function AppAuthProvider({ children }: { children: ReactNode }) {
  if (!isClerkConfigured()) {
    return (
      <AppAuthContext.Provider value={unauthenticatedState}>{children}</AppAuthContext.Provider>
    );
  }

  return <ClerkAuthBridge>{children}</ClerkAuthBridge>;
}

export function useAppAuth(): AppAuthState {
  return useContext(AppAuthContext);
}
