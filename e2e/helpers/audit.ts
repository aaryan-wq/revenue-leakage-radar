import type { Page } from "@playwright/test";
import { expect } from "@playwright/test";

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

export async function ensureOnValidation(page: Page): Promise<void> {
  if (page.url().includes("/validation")) return;

  const continueBtn = page.getByRole("button", { name: "Continue to Validation" });
  if (await continueBtn.isVisible().catch(() => false)) {
    await continueBtn.click();
  }

  await page.waitForURL(/\/validation/, { timeout: 90_000 });
}

export async function uploadCsvFiles(page: Page, filePaths: string[]): Promise<void> {
  await page.goto("/upload");
  await page.getByText("Drop your billing and CRM CSVs here").waitFor({ state: "visible" });

  const fileInput = page.locator('input[type="file"][accept=".csv"]');
  await fileInput.setInputFiles(filePaths);

  for (const filePath of filePaths) {
    const name = filePath.split(/[/\\]/).pop()!;
    await page.getByText(name).first().waitFor({ state: "visible" });
  }

  const uploadBtn = page.getByRole("button", { name: "Upload Files" });
  await expect(uploadBtn).toBeEnabled({ timeout: 30_000 });
  await uploadBtn.click();

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
