import { clerkSetup } from "@clerk/testing/playwright";
import { chromium, test as setup } from "@playwright/test";
import fs from "fs";
import path from "path";

import { ensureClerkTestUser, signInTestUser } from "./helpers/auth";
import { isClerkConfigured, isE2EUserConfigured } from "./helpers/env";

setup.describe.configure({ mode: "serial" });

const authDir = path.join(__dirname, ".auth");
const authFile = path.join(authDir, "user.json");
const baseURL = process.env.PLAYWRIGHT_BASE_URL ?? "http://localhost:3000";

setup("prepare auth directory", async () => {
  if (!fs.existsSync(authDir)) {
    fs.mkdirSync(authDir, { recursive: true });
  }

  const clerkConfigured = isClerkConfigured();

  if (clerkConfigured) {
    try {
      await clerkSetup();
      if (isE2EUserConfigured()) {
        await ensureClerkTestUser();
      }
    } catch (error) {
      console.warn("Clerk setup failed; anonymous E2E only:", error);
    }
  }

  if (!fs.existsSync(authFile)) {
    fs.writeFileSync(authFile, JSON.stringify({ cookies: [], origins: [] }));
  }
});

setup("authenticate test user", async () => {
  if (!isClerkConfigured() || !isE2EUserConfigured()) {
    return;
  }

  const browser = await chromium.launch();
  const context = await browser.newContext();
  const page = await context.newPage();

  try {
    await signInTestUser(page);
    await page.goto("/dashboard");
    await page.waitForURL(/\/dashboard/, { timeout: 30_000 });
    await context.storageState({ path: authFile });
  } catch (error) {
    console.warn("Could not persist auth storage state:", error);
    fs.writeFileSync(authFile, JSON.stringify({ cookies: [], origins: [] }));
  } finally {
    await browser.close();
  }
});

setup("verify app reachable", async ({ request }) => {
  const apiUrl = process.env.PLAYWRIGHT_API_URL ?? process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const health = await request.get(`${apiUrl}/health`);
  if (!health.ok()) {
    throw new Error(`API not reachable at ${apiUrl}/health`);
  }

  const home = await request.get(baseURL);
  if (!home.ok()) {
    throw new Error(`Web app not reachable at ${baseURL}`);
  }
});
