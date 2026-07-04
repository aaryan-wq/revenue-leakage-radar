import { setupClerkTestingToken } from "@clerk/testing/playwright";
import { test, expect } from "@playwright/test";

import { signInTestUser, signOutTestUser } from "./helpers/auth";
import { isClerkConfigured } from "./helpers/env";

test.describe("Authentication lifecycle", () => {
  test.skip(!isClerkConfigured(), "Clerk keys not configured");

  test("sign-in page renders Clerk component", async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await setupClerkTestingToken({ page });
    await page.goto("/sign-in");
    await expect(page.locator(".cl-signIn-root, [data-clerk-component='SignIn']").first()).toBeAttached({
      timeout: 30_000,
    });
  });

  test("sign-up page renders Clerk component", async ({ page }) => {
    await setupClerkTestingToken({ page });
    await page.goto("/sign-up");
    await expect(page.locator('[data-clerk-component="SignUp"], .cl-rootBox').first()).toBeVisible({
      timeout: 30_000,
    });
  });

  test("protected /dashboard redirects unauthenticated users", async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto("/dashboard");
    await page.waitForURL(/sign-in/, { timeout: 30_000 });
  });

  test("protected /billing redirects unauthenticated users", async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto("/billing");
    await page.waitForURL(/sign-in/, { timeout: 30_000 });
  });

  test("protected /account redirects unauthenticated users", async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await page.goto("/account");
    await page.waitForURL(/sign-in/, { timeout: 30_000 });
  });
});

test.describe("Authenticated session", () => {
  test.skip(!isClerkConfigured(), "Clerk keys not configured");

  test.beforeEach(async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });
    await signInTestUser(page);
  });

  test("signed-in user can access dashboard", async ({ page }) => {
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/dashboard/);
    await expect(page.getByRole("heading", { name: /dashboard|audits|reports/i }).first()).toBeVisible({
      timeout: 30_000,
    });
  });

  test("session persists after refresh", async ({ page }) => {
    await page.goto("/dashboard");
    await page.reload();
    await expect(page).toHaveURL(/\/dashboard/);
  });
});

test.describe("Programmatic sign-in", () => {
  test.skip(!isClerkConfigured(), "Clerk keys not configured");

  test("sign in and sign out via Clerk testing helper", async ({ page }) => {
    await page.context().clearCookies();
    await page.addInitScript(() => {
      localStorage.clear();
      sessionStorage.clear();
    });

    await signInTestUser(page);
    await page.goto("/dashboard");
    await expect(page).toHaveURL(/\/dashboard/);

    await signOutTestUser(page);
    await page.goto("/dashboard");
    await page.waitForURL(/sign-in/, { timeout: 30_000 });
  });
});
