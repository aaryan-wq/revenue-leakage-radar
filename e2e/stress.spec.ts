import { test, expect } from "@playwright/test";

import { clearAuditSession } from "./helpers/audit";

test.describe("Browser Stress", () => {
  test.beforeEach(async ({ page }) => {
    await clearAuditSession(page);
  });

  test("rapid button clicks on landing page", async ({ page }) => {
    await page.goto("/");
    const cta = page.getByRole("link", { name: /start audit|upload|get started/i }).first();
    for (let i = 0; i < 5; i++) {
      await cta.click({ force: true, timeout: 2000 }).catch(() => undefined);
    }
    await expect(page.locator("body")).toBeVisible();
  });

  test("repeated page refresh on upload", async ({ page }) => {
    await page.goto("/upload");
    for (let i = 0; i < 5; i++) {
      await page.reload();
    }
    await expect(page.getByText("Drop your billing and CRM CSVs here")).toBeVisible();
  });

  test("navigate away during upload init", async ({ page }) => {
    await page.goto("/upload");
    await page.goto("/pricing");
    await page.goto("/upload");
    await expect(page.getByText("Drop your billing and CRM CSVs here")).toBeVisible();
  });
});
