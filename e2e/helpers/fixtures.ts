import fs from "fs";
import path from "path";

const API_FIXTURES = path.resolve(__dirname, "../../apps/api/tests/fixtures");
const E2E_FIXTURES = path.resolve(__dirname, "../fixtures");

export function fixturePath(filename: string): string {
  const e2ePath = path.join(E2E_FIXTURES, filename);
  if (fs.existsSync(e2ePath)) return e2ePath;
  return path.join(API_FIXTURES, filename);
}

export const TIER0_FILES = ["invoice_line_items.csv", "price_catalog.csv"] as const;

export const FULL_DATASET_FILES = [
  "invoice_line_items.csv",
  "price_catalog.csv",
  "subscriptions.csv",
  "invoices.csv",
  "customers.csv",
  "coupons.csv",
] as const;

export function writeTempCsv(dir: string, filename: string, content: string): string {
  const filePath = path.join(dir, filename);
  fs.writeFileSync(filePath, content, "utf-8");
  return filePath;
}
