import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

export const UPLOAD_ZONE_HEADING = /place your data here/i;
export const CONTINUE_TO_VALIDATION = /continue to validation/i;

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

export async function waitForUploadPageReady(page: Page): Promise<void> {
  await page.goto("/upload");
  await page.getByText(UPLOAD_ZONE_HEADING).waitFor({ state: "visible", timeout: 60_000 });
  await page.getByText(/preparing upload session/i).waitFor({ state: "hidden", timeout: 60_000 }).catch(() => undefined);
}

export async function waitForFilesUploaded(page: Page, fileNames: string[]): Promise<void> {
  const continueBtn = page.getByRole("button", { name: CONTINUE_TO_VALIDATION });
  await expect(continueBtn).toBeEnabled({ timeout: 120_000 });

  for (const filePath of fileNames) {
    const name = filePath.split(/[/\\]/).pop()!;
    await page.getByRole("button", { name: new RegExp(`remove ${name}`, "i") }).waitFor({
      state: "visible",
      timeout: 60_000,
    });
  }
}

export async function ensureOnValidation(page: Page): Promise<void> {
  if (page.url().includes("/validation")) return;

  const continueBtn = page.getByRole("button", { name: CONTINUE_TO_VALIDATION });
  if (await continueBtn.isVisible().catch(() => false)) {
    await expect(continueBtn).toBeEnabled({ timeout: 90_000 });
    await continueBtn.click();
  }

  await page.waitForURL(/\/validation/, { timeout: 90_000 });
}

export async function uploadCsvFiles(page: Page, filePaths: string[]): Promise<void> {
  await waitForUploadPageReady(page);

  const fileInput = page.locator('input[type="file"][accept=".csv"]');
  await fileInput.setInputFiles(filePaths);
  await waitForFilesUploaded(page, filePaths);
  await ensureOnValidation(page);
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
