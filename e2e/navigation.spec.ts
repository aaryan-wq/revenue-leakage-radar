import { test, expect } from "@playwright/test";

import { clearAuditSession } from "./helpers/audit";

const PUBLIC_PAGES = [
  { path: "/", title: /paevo|detect recoverable/i },
  { path: "/upload", title: /upload|billing.*crm|csv/i },
  { path: "/pricing", title: /pricing/i },
  { path: "/security", title: /security/i },
  { path: "/faq", title: /faq|frequently/i },
  { path: "/contact", title: /contact/i },
  { path: "/privacy", title: /privacy/i },
  { path: "/terms", title: /terms/i },
  { path: "/checkout/cancel", title: /cancel|checkout/i },
];

test.describe("Navigation", () => {
  test.beforeEach(async ({ page }) => {
    await clearAuditSession(page);
  });

  for (const { path, title } of PUBLIC_PAGES) {
    test(`loads ${path} without console errors`, async ({ page }) => {
      const errors: string[] = [];
      page.on("console", (msg) => {
        if (msg.type() === "error") errors.push(msg.text());
      });
      page.on("pageerror", (err) => errors.push(err.message));

      const response = await page.goto(path);
      expect(response?.status()).toBeLessThan(400);
      await expect(page.locator("body")).toBeVisible();
      await expect(page.getByRole("link", { name: /paevo/i }).first()).toBeVisible();

      const criticalErrors = errors.filter(
        (e) =>
          !e.includes("favicon") &&
          !e.includes("Clerk") &&
          !e.includes("hydration") &&
          !e.includes("ResizeObserver"),
      );
      expect(criticalErrors, `Console errors on ${path}: ${criticalErrors.join("; ")}`).toEqual([]);
    });
  }

  test("top nav links are not dead", async ({ page }) => {
    await page.goto("/");
    const nav = page.getByRole("navigation");
    const links = [
      nav.getByRole("link", { name: "Pricing", exact: true }),
      nav.getByRole("link", { name: "Security", exact: true }),
      nav.getByRole("link", { name: /run free scan/i }),
    ];

    for (const link of links) {
      await expect(link).toBeVisible();
      const href = await link.getAttribute("href");
      expect(href).toBeTruthy();
    }
  });

  test("rapid navigation does not crash", async ({ page }) => {
    const routes = ["/", "/upload", "/pricing", "/security", "/faq", "/contact"];
    for (let i = 0; i < 3; i++) {
      for (const route of routes) {
        await page.goto(route);
        await page.waitForLoadState("domcontentloaded");
      }
    }
    await expect(page.locator("body")).toBeVisible();
  });
});
