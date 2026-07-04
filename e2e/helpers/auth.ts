import { clerk } from "@clerk/testing/playwright";
import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

import { isClerkConfigured, isE2EUserConfigured } from "./env";

export const E2E_USER_EMAIL =
  process.env.E2E_CLERK_USER_EMAIL ?? "e2e+qa@revenueleakageradar.dev";
export const E2E_USER_PASSWORD =
  process.env.E2E_CLERK_USER_PASSWORD ?? "E2eQaTest!2026Secure";

export async function ensureClerkTestUser(): Promise<void> {
  const secretKey = process.env.CLERK_SECRET_KEY;
  if (!secretKey || secretKey.includes("your_key_here")) return;

  const createResponse = await fetch("https://api.clerk.com/v1/users", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${secretKey}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email_address: [E2E_USER_EMAIL],
      password: E2E_USER_PASSWORD,
      skip_password_checks: true,
      skip_password_requirement: true,
    }),
  });

  if (createResponse.ok) {
    return;
  }

  const createBody = await createResponse.text();
  if (createResponse.status === 422 && createBody.includes("already")) {
    return;
  }

  const listResponse = await fetch(
    `https://api.clerk.com/v1/users?email_address=${encodeURIComponent(E2E_USER_EMAIL)}&limit=1`,
    {
      headers: { Authorization: `Bearer ${secretKey}` },
    },
  );

  if (listResponse.ok) {
    const users = (await listResponse.json()) as unknown[];
    if (users.length > 0) {
      return;
    }
  }

  throw new Error(`Failed to ensure Clerk test user (${createResponse.status}): ${createBody}`);
}

async function waitForSignedIn(page: Page): Promise<void> {
  await page.waitForFunction(
    () => {
      const clerkUser = (window as Window & { Clerk?: { user?: { id?: string } | null } }).Clerk?.user;
      return Boolean(clerkUser?.id);
    },
    { timeout: 30_000 },
  );
}

export async function signInTestUser(page: Page): Promise<void> {
  if (!isClerkConfigured() || !isE2EUserConfigured()) {
    throw new Error("Clerk or E2E user credentials not configured");
  }

  await page.goto("/");
  await clerk.loaded({ page });

  const alreadySignedIn = await page.evaluate(
    () => Boolean((window as Window & { Clerk?: { user?: { id?: string } | null } }).Clerk?.user?.id),
  );
  if (alreadySignedIn) {
    return;
  }

  await clerk.signIn({ page, emailAddress: E2E_USER_EMAIL });
  await waitForSignedIn(page);
}

export async function signOutTestUser(page: Page): Promise<void> {
  await page.goto("/");
  await clerk.loaded({ page });
  await clerk.signOut({ page });
  await expect
    .poll(async () =>
      page.evaluate(
        () => (window as Window & { Clerk?: { user?: { id?: string } | null } }).Clerk?.user?.id ?? null,
      ),
    )
    .toBeNull();
}
