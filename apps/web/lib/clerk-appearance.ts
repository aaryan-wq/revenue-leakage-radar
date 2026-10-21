import type { Appearance } from "@clerk/types";

/** White surface, forest green accent. Matches globals.css. */
export const clerkAppearance: Appearance = {
  variables: {
    colorPrimary: "oklch(0.4 0.085 163)",
    colorDanger: "oklch(0.55 0.2 25)",
    colorSuccess: "oklch(0.4 0.085 163)",
    colorWarning: "oklch(0.62 0.14 55)",
    colorBackground: "oklch(1 0 0)",
    colorInputBackground: "oklch(1 0 0)",
    colorInputText: "oklch(0.18 0.01 160)",
    colorText: "oklch(0.18 0.01 160)",
    colorTextSecondary: "oklch(0.48 0 0)",
    colorNeutral: "oklch(0.48 0 0)",
    borderRadius: "0.5rem",
    fontFamily: "var(--font-geist-sans), system-ui, sans-serif",
    fontFamilyButtons: "var(--font-geist-sans), system-ui, sans-serif",
  },
  elements: {
    rootBox: "font-sans",
    card: "bg-card border border-line shadow-none",
    headerTitle: "font-heading",
    headerSubtitle: "text-muted-foreground",
    formButtonPrimary: "rounded-lg bg-primary text-primary-foreground shadow-none",
    formFieldInput: "border-line bg-card",
    footerActionLink: "text-primary",
    socialButtonsBlockButton: "border-line",
  },
};
