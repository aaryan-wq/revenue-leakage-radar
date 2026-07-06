import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

export const UPLOAD_ZONE_HEADING = "Place your data here";

export async function clearAuditSession(page: Page): Promise<void> {
  await page.goto("/");
  await page.evaluate(() => {
    localStorage.removeItem("rlr_audit_id");
    localStorage.removeItem("rlr_audit_session");
  });
}

export async function waitForApiHealthy(request: { get: (url: string) => Promise<{ ok: () => boolean }> }): Promise<void> {
  const apiUrl = process.env.PLAYWRIGHT_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const response = await request.get(`${apiUrl}/health`);
  if (!response.ok()) {
    throw new Error(`API health check failed at ${apiUrl}/health`);
  }
}

export async function waitForUploadZone(page: Page): Promise<void> {
  await page.getByRole("heading", { name: UPLOAD_ZONE_HEADING }).waitFor({ state: "visible" });
}

export async function waitForAutoUploadComplete(page: Page, fileNames: string[]): Promise<void> {
  for (const name of fileNames) {
    await page.getByText(name).first().waitFor({ state: "visible", timeout: 60_000 });
  }

  const continueBtn = page.getByRole("button", { name: /Continue to Validation/i });
  await expect(continueBtn).toBeVisible({ timeout: 90_000 });
  await expect(continueBtn).toBeEnabled({ timeout: 90_000 });
}

export async function ensureOnValidation(page: Page): Promise<void> {
  if (page.url().includes("/validation")) return;

  try {
    await page.waitForURL(/\/validation/, { timeout: 3_000 });
    return;
  } catch {
    // Still on upload; click through if needed.
  }

  const continueBtn = page.getByRole("button", { name: /Continue to Validation/i });
  if (await continueBtn.isVisible().catch(() => false)) {
    await continueBtn.click({ force: true });
  }

  await page.waitForURL(/\/validation/, { timeout: 90_000 });
}

export async function uploadCsvFiles(page: Page, filePaths: string[]): Promise<void> {
  await page.goto("/upload");
  await waitForUploadZone(page);

  const fileInput = page.locator('input[type="file"][accept=".csv"]');
  await fileInput.setInputFiles(filePaths);

  const names = filePaths.map((filePath) => filePath.split(/[/\\]/).pop()!);
  await waitForAutoUploadComplete(page, names);

  const continueBtn = page.getByRole("button", { name: /Continue to Validation/i });
  await continueBtn.click({ force: true });
  await page.waitForURL(/\/validation/, { timeout: 90_000 });
}

export async function runFullAnonymousPipeline(
  page: Page,
  filePaths: string[],
  options?: { skipSummary?: boolean },
): Promise<void> {
  await uploadCsvFiles(page, filePaths);
  await ensureOnValidation(page);
  await page.getByText(/validation complete|ready with warnings|start scan/i).first().waitFor({
    state: "visible",
    timeout: 120_000,
  });

  const startScan = page.getByRole("button", { name: /start scan/i });
  if (await startScan.isVisible().catch(() => false)) {
    await startScan.click();
  } else {
    const continueLink = page.getByRole("link", { name: /continue to analysis/i });
    if (await continueLink.isVisible().catch(() => false)) {
      await continueLink.click();
    } else {
      await page.goto("/analysis");
    }
  }

  await page.waitForURL(/\/analysis/, { timeout: 30_000 });
  await page.getByText(/scan complete|view full summary|estimated recoverable arr/i).first().waitFor({
    state: "visible",
    timeout: 180_000,
  });

  if (!options?.skipSummary) {
    const summaryLink = page.getByRole("link", { name: /view full summary/i });
    if (await summaryLink.isVisible().catch(() => false)) {
      await summaryLink.click();
      await page.waitForURL(/\/summary/, { timeout: 30_000 });
    }
  }
}
