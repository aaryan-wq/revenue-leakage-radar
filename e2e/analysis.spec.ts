import { test, expect } from "@playwright/test";

import { clearAuditSession, runFullAnonymousPipeline, waitForApiHealthy } from "./helpers/audit";
import { fixturePath } from "./helpers/fixtures";

test.describe("Analysis Workflow", () => {
  test.beforeEach(async ({ page, request }) => {
    await waitForApiHealthy(request);
    await clearAuditSession(page);
  });

  test("completes validation → scan → summary for Tier 0 data", async ({ page }) => {
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await runFullAnonymousPipeline(page, files);

    await expect(page.getByText(/recoverable|annual|revenue|scan complete/i).first()).toBeVisible({
      timeout: 30_000,
    });
    await expect(page.getByText(/verification|coverage/i).first()).toBeVisible();
  });

  test("shows loading states during validation", async ({ page }) => {
    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await page.goto("/upload");
    const fileInput = page.locator('input[type="file"][accept=".csv"]');
    await fileInput.setInputFiles(files);
    await page.getByRole("button", { name: "Upload Files" }).click();

    await page.waitForURL(/\/validation/, { timeout: 90_000 });
    const loadingOrContent = page.getByText(/validat|mapping|processing|ready/i).first();
    await expect(loadingOrContent).toBeVisible({ timeout: 120_000 });
  });

  test("redirects to upload when no audit session on analysis", async ({ page }) => {
    await page.goto("/analysis");
    await page.waitForURL(/\/upload/, { timeout: 15_000 });
  });

  test("redirects to upload when no audit session on summary", async ({ page }) => {
    await page.goto("/summary");
    await page.waitForURL(/\/upload/, { timeout: 15_000 });
  });

  test("refresh during analysis recovers gracefully", async ({ page }) => {
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await page.goto("/upload");
    const fileInput = page.locator('input[type="file"][accept=".csv"]');
    await fileInput.setInputFiles(files);
    await page.getByRole("button", { name: "Upload Files" }).click();
    await page.waitForURL(/\/validation/, { timeout: 90_000 });

    await page.goto("/analysis");
    await page.reload();
    await expect(page.locator("body")).toBeVisible();
    await page.waitForURL(/\/analysis|\/validation|\/upload/, { timeout: 60_000 });
  });
});
