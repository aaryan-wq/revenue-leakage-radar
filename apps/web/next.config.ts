import path from "node:path";
import { fileURLToPath } from "node:url";

import { withSentryConfig } from "@sentry/nextjs";
import { loadEnvConfig } from "@next/env";
import type { NextConfig } from "next";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const monorepoRoot = path.join(__dirname, "../..");

// Monorepo: shared .env lives at repo root; apps/web/.env.local overrides.
loadEnvConfig(monorepoRoot);
loadEnvConfig(__dirname);

const isProductionBuild = process.env.NODE_ENV === "production";

if (isProductionBuild) {
  if (!process.env.NEXT_PUBLIC_API_URL) {
    throw new Error("NEXT_PUBLIC_API_URL must be set for production builds.");
  }
  if (
    !process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY ||
    process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY.includes("your_key_here")
  ) {
    throw new Error("NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY must be set for production builds.");
  }
}

const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY ?? "";
if (!posthogKey && process.env.NODE_ENV !== "test" && !isProductionBuild) {
  console.warn(
    "[analytics] NEXT_PUBLIC_POSTHOG_KEY is missing. Add it to apps/web/.env.local and restart `npm run dev`.",
  );
}

const nextConfig: NextConfig = {
  transpilePackages: ["@rlr/shared"],
  env: {
    NEXT_PUBLIC_POSTHOG_KEY: posthogKey,
    NEXT_PUBLIC_POSTHOG_HOST: process.env.NEXT_PUBLIC_POSTHOG_HOST ?? "https://us.i.posthog.com",
  },
  // Monorepo + ESLint 9 flat config breaks @rushstack/eslint-patch during `next build` on Vercel.
  // Run `npm run lint` locally / in CI instead.
  eslint: {
    ignoreDuringBuilds: true,
  },
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion", "@clerk/nextjs"],
  },
};

export default withSentryConfig(nextConfig, {
  silent: true,
  disableLogger: true,
});
