import Link from "next/link";

import { SiteFooter } from "@/components/marketing/site-footer";
import { GlassCard } from "@/components/ui/glass-card";

export default function PrivacyPage() {
  return (
    <>
      <main className="mx-auto max-w-reading px-8 py-24">
        <h1 className="text-h1 text-primary">Privacy Policy</h1>
        <p className="mt-4 text-caption text-gray-500">Last updated: June 2026</p>

        <GlassCard padding="md" className="mt-12 space-y-8">
          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Overview</h2>
            <p className="mt-3 text-body text-gray-600">
              Revenue Leakage Radar (&quot;we&quot;, &quot;us&quot;) provides revenue verification software for
              finance teams. This policy describes how we collect, use, and protect information when you use
              our service.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Data You Provide</h2>
            <p className="mt-3 text-body text-gray-600">
              When you upload billing CSV exports, we process that data to run deterministic verification
              checks and generate reports. Account information is managed through our authentication
              provider (Clerk). Payment information is processed by Stripe — we do not store full card
              details.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">CSV Retention</h2>
            <p className="mt-3 text-body text-gray-600">
              Raw uploaded CSV files are stored only during active processing and are automatically deleted
              after ingestion completes. Canonical billing data required for reports is retained in our
              database until you delete the associated audit.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">How We Use Data</h2>
            <ul className="mt-3 list-disc space-y-2 pl-6 text-body text-gray-600">
              <li>Run revenue verification rules and generate summaries and reports</li>
              <li>Provide AI-assisted column mapping and executive narratives (not financial calculations)</li>
              <li>Process payments and manage report entitlements</li>
              <li>Improve product reliability and security</li>
            </ul>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Security</h2>
            <p className="mt-3 text-body text-gray-600">
              We use HTTPS encryption in transit and provider-managed encryption at rest. See our{" "}
              <Link href="/security" className="text-primary underline-offset-4 hover:underline">
                Security page
              </Link>{" "}
              for more detail.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Contact</h2>
            <p className="mt-3 text-body text-gray-600">
              Questions about this policy? Contact us at{" "}
              <a href="mailto:support@revenueleakageradar.com" className="text-primary hover:underline">
                support@revenueleakageradar.com
              </a>
              .
            </p>
          </section>

          <p className="text-small text-gray-400">
            This is a template privacy policy for MVP purposes. Have it reviewed by qualified legal counsel
            before production launch.
          </p>
        </GlassCard>
      </main>
      <SiteFooter />
    </>
  );
}
