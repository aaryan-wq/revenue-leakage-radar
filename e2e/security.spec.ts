import { test, expect } from "@playwright/test";

import { apiBaseUrl } from "./helpers/env";

test.describe("Security", () => {
  test("API rejects unauthenticated dashboard access", async ({ request }) => {
    const response = await request.get(`${apiBaseUrl()}/dashboard`);
    expect([401, 403]).toContain(response.status());
  });

  test("API rejects forged report export without entitlement", async ({ request }) => {
    const fakeReportId = "00000000-0000-0000-0000-000000000099";
    const response = await request.get(`${apiBaseUrl()}/exports/pdf/${fakeReportId}`);
    expect([401, 403, 404]).toContain(response.status());
  });

  test("API rejects checkout without valid report", async ({ request }) => {
    const response = await request.post(`${apiBaseUrl()}/checkout`, {
      data: { report_id: "00000000-0000-0000-0000-000000000099", product: "single_report" },
      headers: { "Content-Type": "application/json" },
    });
    expect([400, 401, 403, 404, 422]).toContain(response.status());
  });

  test("direct URL to fake report page does not expose data", async ({ page }) => {
    await page.goto("/report/00000000-0000-0000-0000-000000000099");
    await expect(page.getByText(/unavailable|not found|sign in|locked|error/i).first()).toBeVisible({
      timeout: 30_000,
    });
  });

  test("direct URL to fake finding does not expose data", async ({ page }) => {
    await page.goto("/findings/00000000-0000-0000-0000-000000000099");
    await expect(page.getByText(/unavailable|not found|sign in|locked|error/i).first()).toBeVisible({
      timeout: 30_000,
    });
  });

  test("manipulated audit ID in API returns 404 or 403", async ({ request }) => {
    const response = await request.get(`${apiBaseUrl()}/audit/00000000-0000-0000-0000-000000000099`, {
      headers: { "X-Audit-Session": "invalid-token" },
    });
    expect([403, 404]).toContain(response.status());
  });
});
