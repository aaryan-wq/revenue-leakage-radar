import { test, expect } from "@playwright/test";

import { getSummaryForAudit } from "./helpers/api";
import { clearAuditSession, runGoldenPipeline, waitForApiHealthy } from "./helpers/audit";

/** Ground truth from testdata/runs/run_991337/README.md */
const GOLDEN_ANNUAL_ARR = 134_023.56;
const GOLDEN_ARR_TOLERANCE = 0.15;

test.describe("Golden audit run_991337", () => {
  test.beforeEach(async ({ page, request }) => {
    await waitForApiHealthy(request);
    await clearAuditSession(page);
  });

  test("full upload scan produces deterministic findings", async ({ page, request }) => {
    test.setTimeout(600_000);

    await runGoldenPipeline(page);

    const auditId = await page.evaluate(() => localStorage.getItem("rlr_audit_id"));
    const sessionToken = await page.evaluate(() => localStorage.getItem("rlr_audit_session"));
    expect(auditId).toBeTruthy();
    expect(sessionToken).toBeTruthy();

    const summary = await getSummaryForAudit(request, auditId!, { sessionToken });
    expect(summary.report_id).toBeTruthy();
    expect(summary.finding_count).toBeGreaterThanOrEqual(20);

    const recoverableArr = Number(summary.recoverable_arr ?? 0);
    expect(recoverableArr).toBeGreaterThan(0);
    const delta = Math.abs(recoverableArr - GOLDEN_ANNUAL_ARR) / GOLDEN_ANNUAL_ARR;
    expect(delta).toBeLessThanOrEqual(GOLDEN_ARR_TOLERANCE);
  });
});
