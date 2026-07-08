export const PRODUCT_NAMES = {
  freeAudit: "Free Audit",
  verificationReport: "Revenue Verification Report",
  enterprise: "Enterprise",
} as const;

export const VERIFICATION_REPORT_PRICE = "$2,500";

export const PRICING_TIERS = {
  free: {
    label: PRODUCT_NAMES.freeAudit,
    price: "$0",
    priceNote: null as string | null,
    description: "Get a fast topline leakage scan from your uploaded revenue data.",
    features: [
      "Recoverable ARR estimate",
      "Monthly leakage estimate",
      "Leakage category summary",
      "Coverage score + confidence indicators",
      "Redacted findings preview",
      "No account required to start",
    ],
    cta: "Run Free Audit",
  },
  verificationReport: {
    label: PRODUCT_NAMES.verificationReport,
    price: VERIFICATION_REPORT_PRICE,
    priceNote: "/ audit",
    description:
      "A full evidence-backed audit showing exactly where revenue is leaking and how much can be recovered.",
    features: [
      "Full detailed findings",
      "Evidence + calculation trace",
      "Customer / subscription / invoice-level detail where available",
      "Downloadable report + findings export",
      "Coverage report + remediation view",
      "Workspace access for the purchased audit",
    ],
    cta: "Unlock Full Report",
  },
  enterprise: {
    label: PRODUCT_NAMES.enterprise,
    price: "Custom",
    priceNote: null as string | null,
    description:
      "Continuous revenue assurance for teams that want recurring audits, integrations, and a shared workspace.",
    features: [
      "Recurring audits",
      "API integrations",
      "Historical comparisons",
      "Team workspace",
      "Priority support",
      "Security / procurement support",
    ],
    cta: "Talk to Sales",
  },
} as const;

export const PRICING_PREVIEW_TIERS = [
  {
    name: PRODUCT_NAMES.freeAudit,
    price: "$0",
    note: "No account required to start",
    highlight: "Topline leakage scan with recoverable ARR and category summary",
  },
  {
    name: PRODUCT_NAMES.verificationReport,
    price: `${VERIFICATION_REPORT_PRICE} / audit`,
    note: "One dataset · full evidence",
    highlight: "Detailed findings, calculation trace, and downloadable exports",
  },
  {
    name: PRODUCT_NAMES.enterprise,
    price: "Custom",
    note: "Talk to sales",
    highlight: "Recurring audits, integrations, and team workspace",
  },
] as const;

export function planDisplayName(plan: string): string {
  if (plan === "annual") {
    return `${PRODUCT_NAMES.enterprise} (Annual)`;
  }
  if (plan === "none") {
    return "Pay per audit";
  }
  if (plan === "single_report") {
    return PRODUCT_NAMES.verificationReport;
  }
  return plan.replace(/_/g, " ");
}
