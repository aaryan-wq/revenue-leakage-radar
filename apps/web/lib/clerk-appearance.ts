import type { Appearance } from "@clerk/types";

/** Warm paper + emerald. Matches globals.css design tokens */
export const clerkAppearance: Appearance = {
  variables: {
    colorPrimary: "oklch(0.455 0.078 165)",
    colorDanger: "oklch(0.55 0.18 28)",
    colorSuccess: "oklch(0.455 0.078 165)",
    colorWarning: "oklch(0.68 0.135 55)",
    colorBackground: "oklch(0.985 0.005 95)",
    colorInputBackground: "oklch(0.997 0.003 95)",
    colorInputText: "oklch(0.235 0.012 75)",
    colorText: "oklch(0.235 0.012 75)",
    colorTextSecondary: "oklch(0.53 0.012 80)",
    colorNeutral: "oklch(0.53 0.012 80)",
    borderRadius: "0.5rem",
    fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
    fontFamilyButtons: "var(--font-geist-sans), system-ui, sans-serif",
  },
  elements: {
    rootBox: "font-sans",
    card: "bg-card border border-line shadow-none",
    headerTitle: "font-heading tracking-tight",
    headerSubtitle: "text-muted-foreground",
    formButtonPrimary:
      "rounded-full bg-primary text-primary-foreground shadow-[0_12px_40px_-10px] shadow-primary/40 hover:shadow-[0_16px_50px_-12px] hover:shadow-primary/50",
    formFieldInput: "border-line bg-card",
    footerActionLink: "text-primary",
    socialButtonsBlockButton: "border-line",
  },
};
