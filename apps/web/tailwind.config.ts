import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
    "../../packages/ui/src/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        white: "#FFFFFF",
        gray: {
          25: "#FCFCFD",
          50: "#F8FAFC",
          100: "#F1F5F9",
          200: "#E2E8F0",
          300: "#CBD5E1",
          400: "#94A3B8",
          500: "#64748B",
          700: "#334155",
          900: "#0F172A",
        },
        primary: {
          DEFAULT: "#0F172A",
          hover: "#1E293B",
          active: "#020617",
          light: "#F8FAFC",
        },
        blue: {
          DEFAULT: "#2563EB",
          hover: "#1D4ED8",
          light: "#EFF6FF",
        },
        success: {
          DEFAULT: "#16A34A",
          bg: "#F0FDF4",
        },
        warning: {
          DEFAULT: "#D97706",
          bg: "#FFFBEB",
        },
        error: {
          DEFAULT: "#DC2626",
          bg: "#FEF2F2",
        },
        info: {
          DEFAULT: "#0284C7",
          bg: "#F0F9FF",
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-xl": ["4rem", { lineHeight: "1", fontWeight: "700", letterSpacing: "-0.04em" }],
        display: ["3rem", { lineHeight: "1.05", fontWeight: "700", letterSpacing: "-0.04em" }],
        h1: ["2.25rem", { lineHeight: "1.1", fontWeight: "700", letterSpacing: "-0.03em" }],
        h2: ["1.875rem", { lineHeight: "1.2", fontWeight: "650", letterSpacing: "-0.025em" }],
        h3: ["1.5rem", { lineHeight: "1.25", fontWeight: "650", letterSpacing: "-0.02em" }],
        h4: ["1.25rem", { lineHeight: "1.3", fontWeight: "600", letterSpacing: "-0.02em" }],
        large: ["1.125rem", { lineHeight: "1.5", fontWeight: "500", letterSpacing: "-0.01em" }],
        body: ["1rem", { lineHeight: "1.6", fontWeight: "400", letterSpacing: "-0.01em" }],
        small: ["0.875rem", { lineHeight: "1.5", fontWeight: "400" }],
        caption: ["0.75rem", { lineHeight: "1.4", fontWeight: "500" }],
      },
      spacing: {
        1: "0.25rem",
        2: "0.5rem",
        3: "0.75rem",
        4: "1rem",
        5: "1.25rem",
        6: "1.5rem",
        8: "2rem",
        10: "2.5rem",
        12: "3rem",
        16: "4rem",
        20: "5rem",
        24: "6rem",
      },
      borderRadius: {
        button: "12px",
        card: "18px",
        input: "12px",
        table: "16px",
        modal: "24px",
      },
      boxShadow: {
        card: "0 1px 3px rgba(15,23,42,0.05)",
        "card-hover": "0 10px 30px rgba(15,23,42,0.08)",
        modal: "0 30px 60px rgba(15,23,42,0.12)",
      },
      maxWidth: {
        container: "1280px",
        reading: "760px",
      },
      transitionDuration: {
        fast: "150ms",
        normal: "200ms",
        slow: "300ms",
      },
    },
  },
  plugins: [],
};

export default config;
