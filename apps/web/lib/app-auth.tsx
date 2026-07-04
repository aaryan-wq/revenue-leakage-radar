"use client";

import { useAuth as useClerkAuth } from "@clerk/nextjs";
import { createContext, useCallback, useContext, type ReactNode } from "react";

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
  const { isLoaded, isSignedIn, getToken: clerkGetToken } = useClerkAuth();

  const getToken = useCallback(async (): Promise<string | null> => {
    let token = await clerkGetToken();
    if (!token && isSignedIn) {
      // Session JWT can lag slightly behind isSignedIn on first paint.
      await new Promise((resolve) => setTimeout(resolve, 150));
      token = await clerkGetToken({ skipCache: true });
    }
    return token;
  }, [clerkGetToken, isSignedIn]);

  const value: AppAuthState = {
    isLoaded,
    isSignedIn: isSignedIn ?? false,
    getToken,
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
