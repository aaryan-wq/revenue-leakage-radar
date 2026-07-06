import { test, expect } from "@playwright/test";

import { clearAuditSession, UPLOAD_ZONE_HEADING, waitForUploadPageReady } from "./helpers/audit";

test.describe("Browser Stress", () => {
  test.beforeEach(async ({ page }) => {
    await clearAuditSession(page);
  });

  test("rapid button clicks on landing page", async ({ page }) => {
    await page.goto("/");
    const cta = page.getByRole("link", { name: /run free audit|start audit|upload|get started/i }).first();
    for (let i = 0; i < 5; i++) {
      await cta.click({ force: true, timeout: 2000 }).catch(() => undefined);
    }
    await expect(page.locator("body")).toBeVisible();
  });

  test("repeated page refresh on upload", async ({ page }) => {
    await waitForUploadPageReady(page);
    for (let i = 0; i < 5; i++) {
      await page.reload();
    }
    await expect(page.getByText(UPLOAD_ZONE_HEADING)).toBeVisible();
  });

  test("navigate away during upload init", async ({ page }) => {
    await waitForUploadPageReady(page);
    await page.goto("/pricing");
    await page.goto("/upload");
    await expect(page.getByText(UPLOAD_ZONE_HEADING)).toBeVisible();
  });
});
