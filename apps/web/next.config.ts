import path from "node:path";
import { fileURLToPath } from "node:url";

import { loadEnvConfig } from "@next/env";
import type { NextConfig } from "next";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const monorepoRoot = path.join(__dirname, "../..");

// Monorepo: shared .env lives at repo root; apps/web/.env.local overrides.
loadEnvConfig(monorepoRoot);
loadEnvConfig(__dirname);

const posthogKey = process.env.NEXT_PUBLIC_POSTHOG_KEY ?? "";
if (!posthogKey && process.env.NODE_ENV !== "test") {
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
  experimental: {
    optimizePackageImports: ["lucide-react", "framer-motion", "@clerk/nextjs"],
  },
};

export default nextConfig;
