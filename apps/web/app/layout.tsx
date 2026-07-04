import type { Metadata } from "next";
import { Fraunces, Geist, Geist_Mono } from "next/font/google";

import { AppProviders } from "@/components/providers/app-providers";
import { ClerkProviderWrapper } from "@/components/providers/clerk-provider";

import "./globals.css";

const geistSans = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
});

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-geist-mono",
});

const fraunces = Fraunces({
  subsets: ["latin"],
  variable: "--font-fraunces",
  axes: ["opsz", "SOFT", "WONK"],
});

export const metadata: Metadata = {
  title: "Paevo",
  description: "Detect recoverable recurring revenue from billing and CRM data.",
  icons: {
    icon: "/brand/logo-short.png",
    apple: "/brand/logo-short.png",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} ${fraunces.variable} bg-background`}
    >
      <body className="font-sans antialiased">
        <ClerkProviderWrapper>
          <AppProviders>{children}</AppProviders>
        </ClerkProviderWrapper>
      </body>
    </html>
  );
}
