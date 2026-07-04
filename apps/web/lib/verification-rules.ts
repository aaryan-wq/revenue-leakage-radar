/** Marketing + product copy for the live verification ruleset (v2.0, 25 rules). */

export const VERIFICATION_RULE_COUNT = 25;

export type VerificationRuleSummary = {
  name: string;
  detail: string;
};

export type VerificationRuleCategory = {
  label: string;
  description: string;
  checks: VerificationRuleSummary[];
};

export const VERIFICATION_RULE_CATEGORIES: VerificationRuleCategory[] = [
  {
    label: "Pricing",
    description: "Catalog truth vs what customers are actually billed.",
    checks: [
      { name: "Legacy Pricing", detail: "Subscriptions priced below catalog after a newer price became effective." },
      { name: "Price Catalog Mismatch", detail: "Invoice lines billed below the active list price." },
      { name: "Grandfathered Pricing", detail: "Legacy rates with no contract exception on file." },
      { name: "Missing Scheduled Increase", detail: "Contracted uplifts that never hit billing." },
      { name: "Renewal Price Drift", detail: "Renewal invoices priced below the prior period." },
      { name: "Manual Price Override", detail: "Ungoverned line-item overrides below list price." },
      { name: "Incorrect Seat Price", detail: "CRM seat counts exceed billed subscription quantity." },
      { name: "Incorrect Add-on Price", detail: "Add-on lines priced below the active catalog rate." },
    ],
  },
  {
    label: "Discounts",
    description: "Coupon logic, stacking, and discount persistence.",
    checks: [
      { name: "Expired Discount", detail: "Coupons honored past their expiration date." },
      { name: "Discount Stacking", detail: "Multiple discounts compounding on one subscription." },
      { name: "Duplicate Discount", detail: "The same discount applied more than once on a renewal." },
      { name: "Permanent Promotional Discount", detail: "Promotional pricing beyond commercial terms." },
      { name: "Excessive Discount", detail: "Discount frequency above policy thresholds." },
      { name: "Discount Applied to Wrong Product", detail: "Coupon applied to an ineligible product or SKU." },
    ],
  },
  {
    label: "Billing",
    description: "Invoice execution, cadence, and subscription integrity.",
    checks: [
      { name: "Invoice Price Mismatch", detail: "Invoice line unit prices differ from subscription price." },
      { name: "Duplicate Subscription", detail: "Multiple active subscriptions for the same product." },
      { name: "Billing Frequency Mismatch", detail: "Invoice cadence inconsistent with subscription interval." },
      { name: "Active Subscription Not Billing", detail: "Active subscriptions with no invoice history." },
      { name: "Cancelled Subscription Still Billing", detail: "Invoices continuing after cancellation." },
      { name: "Missing Expected Invoice", detail: "Gaps in the expected recurring invoice schedule." },
    ],
  },
  {
    label: "Credits",
    description: "Write-downs and duplicate credit applications.",
    checks: [
      { name: "Credit Leakage", detail: "Credits applied without matching adjustment records." },
      { name: "Duplicate Credit", detail: "The same credit amount applied more than once." },
    ],
  },
  {
    label: "Data quality",
    description: "Cross-record integrity across billing entities.",
    checks: [
      { name: "Duplicate Customer", detail: "Multiple customer records for the same account." },
      { name: "Currency Mismatch", detail: "Mixed currencies across subscription, invoice, and catalog." },
      { name: "Orphaned Records", detail: "Line items or references with missing parent records." },
    ],
  },
];

if (VERIFICATION_RULE_CATEGORIES.reduce((n, c) => n + c.checks.length, 0) !== VERIFICATION_RULE_COUNT) {
  throw new Error("VERIFICATION_RULE_CATEGORIES must list exactly VERIFICATION_RULE_COUNT rules.");
}
