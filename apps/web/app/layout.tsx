import type { Metadata } from "next";
import { Inter } from "next/font/google";

import { AppProviders } from "@/components/providers/app-providers";
import { ClerkProviderWrapper } from "@/components/providers/clerk-provider";

import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Revenue Leakage Radar",
  description: "Detect recoverable recurring revenue from billing data.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={inter.variable}>
      <body>
        <ClerkProviderWrapper>
          <AppProviders>{children}</AppProviders>
        </ClerkProviderWrapper>
      </body>
    </html>
  );
}
