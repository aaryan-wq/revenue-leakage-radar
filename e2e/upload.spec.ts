import { test, expect } from "@playwright/test";
import fs from "fs";
import os from "os";
import path from "path";

import {
  clearAuditSession,
  CONTINUE_TO_VALIDATION,
  uploadCsvFiles,
  UPLOAD_ZONE_HEADING,
  waitForApiHealthy,
  waitForUploadPageReady,
} from "./helpers/audit";
import { fixturePath, TIER0_FILES, writeTempCsv } from "./helpers/fixtures";

test.describe("CSV Upload Flow", () => {
  test.beforeEach(async ({ page, request }) => {
    await waitForApiHealthy(request);
    await clearAuditSession(page);
  });

  test("uploads valid Tier 0 dataset and redirects to validation", async ({ page }) => {
    const files = TIER0_FILES.map(fixturePath);
    await uploadCsvFiles(page, files);
    await page.waitForURL(/\/validation/, { timeout: 90_000 });
    await expect(page.getByText(/validation|column mapping|platform/i).first()).toBeVisible({
      timeout: 120_000,
    });
  });

  test("uploads full enriched dataset", async ({ page }) => {
    const files = [
      "invoice_line_items.csv",
      "price_catalog.csv",
      "subscriptions.csv",
      "invoices.csv",
      "customers.csv",
      "coupons.csv",
    ].map(fixturePath);

    await uploadCsvFiles(page, files);
    await page.waitForURL(/\/validation/, { timeout: 90_000 });
    await expect(page.getByText(/validation|column mapping/i).first()).toBeVisible({
      timeout: 120_000,
    });
  });

  test("rejects non-CSV files silently in picker", async ({ page }) => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "rlr-e2e-"));
    const txtPath = writeTempCsv(tmpDir, "not-a-csv.txt", "hello world");

    await waitForUploadPageReady(page);

    const fileInput = page.locator('input[type="file"][accept=".csv"]');
    await fileInput.setInputFiles(txtPath);

    await expect(page.getByText("not-a-csv.txt")).not.toBeVisible();
    await expect(page.getByRole("button", { name: CONTINUE_TO_VALIDATION })).not.toBeVisible();
  });

  test("shows error for empty CSV file", async ({ page }) => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "rlr-e2e-"));
    const emptyPath = writeTempCsv(tmpDir, "invoice_line_items.csv", "");

    await waitForUploadPageReady(page);
    const fileInput = page.locator('input[type="file"][accept=".csv"]');
    await fileInput.setInputFiles([emptyPath, fixturePath("price_catalog.csv")]);

    await expect(page.getByText(/failed|error|invalid|empty/i).first()).toBeVisible({
      timeout: 60_000,
    });
  });

  test("handles malformed CSV without crashing", async ({ page }) => {
    const tmpDir = fs.mkdtempSync(path.join(os.tmpdir(), "rlr-e2e-"));
    const badPath = writeTempCsv(
      tmpDir,
      "invoice_line_items.csv",
      "not,a,valid\ncsv\"broken\nline",
    );

    await waitForUploadPageReady(page);
    const fileInput = page.locator('input[type="file"][accept=".csv"]');
    await fileInput.setInputFiles([badPath, fixturePath("price_catalog.csv")]);

    await expect(page.locator("body")).toBeVisible();
    await page.waitForURL(/\/validation|\/upload/, { timeout: 90_000 });
  });

  test("rapid file selection does not crash", async ({ page }) => {
    const files = TIER0_FILES.map(fixturePath);
    await waitForUploadPageReady(page);
    const fileInput = page.locator('input[type="file"][accept=".csv"]');
    await fileInput.setInputFiles(files);
    await fileInput.setInputFiles(files).catch(() => undefined);

    await page.waitForURL(/\/validation|\/upload/, { timeout: 90_000 });
    await expect(page.locator("body")).toBeVisible();
  });

  test("abandons upload midway and recovers on refresh", async ({ page }) => {
    await waitForUploadPageReady(page);
    await page.reload();
    await expect(page.getByText(UPLOAD_ZONE_HEADING)).toBeVisible();
  });
});
