import { test, expect } from "@playwright/test";

import { devUnlockReport } from "./helpers/api";
import { clearAuditSession, runFullAnonymousPipeline, waitForApiHealthy } from "./helpers/audit";
import { fixturePath } from "./helpers/fixtures";
import { isClerkConfigured, isStripeConfigured } from "./helpers/env";

test.describe("Checkout cancel", () => {
  test("cancel page loads with recovery actions", async ({ page }) => {
    await page.goto("/checkout/cancel");
    await expect(page.getByText(/cancel|checkout|return|summary/i).first()).toBeVisible();
    await expect(page.locator("body")).toBeVisible();
  });
});

test.describe("Payments and entitlements", () => {
  test.skip(!isClerkConfigured(), "Clerk not configured");

  test.use({ storageState: "e2e/.auth/user.json" });

  test.beforeEach(async ({ page, request }) => {
    await waitForApiHealthy(request);
    await clearAuditSession(page);
  });

  test("signed-in user sees unlock options on summary", async ({ page, request }) => {
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await runFullAnonymousPipeline(page, files);

    await expect(page.getByText(/unlock|purchase|report/i).first()).toBeVisible({ timeout: 30_000 });

    const auditId = await page.evaluate(() => localStorage.getItem("rlr_audit_id"));
    const sessionToken = await page.evaluate(() => localStorage.getItem("rlr_audit_session"));
    const summaryResponse = await request.get(
      `${process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000"}/summary/${auditId}`,
      { headers: { "X-Audit-Session": sessionToken! } },
    );
    const summary = await summaryResponse.json();
    expect(summary.report_id).toBeTruthy();
  });

  test("dev unlock grants report access", async ({ page, request }) => {
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await runFullAnonymousPipeline(page, files);

    const auditId = await page.evaluate(() => localStorage.getItem("rlr_audit_id"));
    const sessionToken = await page.evaluate(() => localStorage.getItem("rlr_audit_session"));
    const summaryResponse = await request.get(
      `${process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000"}/summary/${auditId}`,
      { headers: { "X-Audit-Session": sessionToken! } },
    );
    const summary = await summaryResponse.json();
    const reportId = summary.report_id as string;

    await devUnlockReport(request, reportId);
    await page.goto(`/report/${reportId}`);
    await expect(page.getByText(/report|findings|recoverable|executive/i).first()).toBeVisible({
      timeout: 30_000,
    });
  });

  test("checkout redirects to Stripe when configured", async ({ page, request }) => {
    test.skip(!isStripeConfigured(), "Stripe not configured");
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await runFullAnonymousPipeline(page, files);

    const purchaseBtn = page.getByRole("button", { name: /purchase report/i });
    await purchaseBtn.scrollIntoViewIfNeeded();
    await expect(purchaseBtn).toBeVisible({ timeout: 30_000 });

    const auditId = await page.evaluate(() => localStorage.getItem("rlr_audit_id"));
    const sessionToken = await page.evaluate(() => localStorage.getItem("rlr_audit_session"));
    const summaryResponse = await request.get(
      `${process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000"}/summary/${auditId}`,
      { headers: { "X-Audit-Session": sessionToken! } },
    );
    const summary = await summaryResponse.json();
    expect(summary.report_id).toBeTruthy();

    await purchaseBtn.click();
    await page.waitForURL(/checkout\.stripe\.com|stripe/, { timeout: 60_000 });
    expect(page.url()).toMatch(/stripe/);
  });
});
