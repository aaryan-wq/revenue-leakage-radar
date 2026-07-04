export function isClerkConfigured(): boolean {
  const key = process.env.NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY;
  return Boolean(key && !key.includes("your_key_here"));
}

export function isE2EUserConfigured(): boolean {
  return Boolean(process.env.CLERK_SECRET_KEY && !process.env.CLERK_SECRET_KEY.includes("your_key_here"));
}

export function isStripeConfigured(): boolean {
  return Boolean(
    process.env.STRIPE_SECRET_KEY &&
      process.env.STRIPE_PRICE_SINGLE_REPORT &&
      !process.env.STRIPE_PRICE_SINGLE_REPORT.includes("price_..."),
  );
}

export function apiBaseUrl(): string {
  return process.env.PLAYWRIGHT_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}
