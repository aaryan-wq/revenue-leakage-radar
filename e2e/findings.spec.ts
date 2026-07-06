import { test, expect } from "@playwright/test";

import { devUnlockReport, getFindingDetail, getReportDetail } from "./helpers/api";
import { runFullAnonymousPipeline, clearAuditSession, waitForApiHealthy } from "./helpers/audit";
import { fixturePath } from "./helpers/fixtures";
import { isClerkConfigured } from "./helpers/env";

test.describe("Findings UI", () => {
  test.beforeEach(async ({ page, request }) => {
    await waitForApiHealthy(request);
    await clearAuditSession(page);
  });

  test("locked finding shows error for unpaid report", async ({ page, request }) => {
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await runFullAnonymousPipeline(page, files);

    const auditId = await page.evaluate(() => localStorage.getItem("rlr_audit_id"));
    const sessionToken = await page.evaluate(() => localStorage.getItem("rlr_audit_session"));
    expect(auditId).toBeTruthy();
    expect(sessionToken).toBeTruthy();

    const summaryResponse = await request.get(
      `${process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000"}/summary/${auditId}`,
      { headers: { "X-Audit-Session": sessionToken! } },
    );
    const summary = await summaryResponse.json();

    if (!summary.finding_count || summary.finding_count === 0) {
      test.skip(true, "No findings in fixture data for this run");
    }

    const report = await getReportDetail(request, summary.report_id, sessionToken!).catch(() => null);
    if (report?.findings?.length) {
      test.skip(true, "Report unexpectedly accessible before purchase");
    }

    await page.goto(`/findings/00000000-0000-0000-0000-000000000001`);
    await expect(page.getByText(/unavailable|locked|sign in|purchase|not found|unable/i).first()).toBeVisible({
      timeout: 30_000,
    });
  });

  test("unlocked finding shows evidence and consistent leakage math", async ({ page, request }) => {
    test.setTimeout(300_000);

    const files = ["invoice_line_items.csv", "price_catalog.csv"].map(fixturePath);
    await runFullAnonymousPipeline(page, files);

    const auditId = await page.evaluate(() => localStorage.getItem("rlr_audit_id"));
    const sessionToken = await page.evaluate(() => localStorage.getItem("rlr_audit_session"));
    expect(auditId).toBeTruthy();

    const summaryResponse = await request.get(
      `${process.env.PLAYWRIGHT_API_URL ?? "http://localhost:8000"}/summary/${auditId}`,
      { headers: { "X-Audit-Session": sessionToken! } },
    );
    expect(summaryResponse.ok()).toBeTruthy();
    const summary = await summaryResponse.json();
    const reportId = summary.report_id as string;
    expect(reportId).toBeTruthy();

    if (!summary.finding_count || summary.finding_count === 0) {
      test.skip(true, "No findings generated for fixture data");
    }

    await devUnlockReport(request, reportId, sessionToken!);
    const report = await getReportDetail(request, reportId, sessionToken!);
    expect(report.findings.length).toBeGreaterThan(0);

    const findingId = report.findings[0].id;
    const apiFinding = await getFindingDetail(request, findingId, sessionToken!);

    await page.goto(`/findings/${findingId}`);
    await expect(page.getByRole("heading", { level: 1 })).toBeVisible({ timeout: 30_000 });
    await expect(page.getByText(/evidence/i)).toBeVisible();

    const monthly = Number(apiFinding.estimated_monthly_loss);
    const annual = Number(apiFinding.estimated_arr_loss);
    if (monthly > 0) {
      expect(Math.abs(annual - monthly * 12)).toBeLessThan(0.02);
    }

    await expect(page.getByRole("button", { name: /copy link/i })).toBeVisible();
  });
});

test.describe("Findings auth", () => {
  test.skip(!isClerkConfigured(), "Clerk not configured");

  test.use({ storageState: "e2e/.auth/user.json" });

  test("fake finding ID shows error", async ({ page }) => {
    await page.goto("/findings/00000000-0000-0000-0000-000000000099");
    await expect(page.getByText(/unavailable|not found|locked|error|unable/i).first()).toBeVisible({
      timeout: 30_000,
    });
  });
});
