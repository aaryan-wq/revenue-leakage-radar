import Link from "next/link";

import { SiteFooter } from "@/components/marketing/site-footer";
import { GlassCard } from "@/components/ui/glass-card";

export default function TermsPage() {
  return (
    <>
      <main className="mx-auto max-w-reading px-8 py-24">
        <h1 className="text-h1 text-primary">Terms of Service</h1>
        <p className="mt-4 text-caption text-gray-500">Last updated: June 2026</p>

        <GlassCard padding="md" className="mt-12 space-y-8">
          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Agreement</h2>
            <p className="mt-3 text-body text-gray-600">
              By using Revenue Leakage Radar, you agree to these Terms of Service. If you do not agree, do
              not use the service.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Service Description</h2>
            <p className="mt-3 text-body text-gray-600">
              We provide automated revenue verification analysis of billing data you upload. Findings and
              financial impact estimates are produced by deterministic rules. AI assists with data mapping
              and narrative generation only — it does not make financial decisions.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Your Responsibilities</h2>
            <ul className="mt-3 list-disc space-y-2 pl-6 text-body text-gray-600">
              <li>You must have the right to upload and process the billing data you provide</li>
              <li>You are responsible for validating findings before taking billing or contractual action</li>
              <li>You must not misuse the service or attempt to access other users&apos; data</li>
            </ul>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Payments &amp; Refunds</h2>
            <p className="mt-3 text-body text-gray-600">
              Paid reports and annual memberships are billed through Stripe. Refund requests may be submitted
              within 7 days of purchase for processing errors. See our{" "}
              <Link href="/faq" className="text-primary underline-offset-4 hover:underline">
                FAQ
              </Link>{" "}
              for details.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Disclaimer</h2>
            <p className="mt-3 text-body text-gray-600">
              The service is provided &quot;as is&quot; without warranty. Revenue estimates are indicative
              and based on the data you provide. We are not liable for decisions made based on report
              outputs.
            </p>
          </section>

          <section>
            <h2 className="text-h3 font-semibold text-gray-900">Account Termination</h2>
            <p className="mt-3 text-body text-gray-600">
              You may delete your account through your account settings. We may suspend access for violation
              of these terms.
            </p>
          </section>

          <p className="text-small text-gray-400">
            This is a template terms of service for MVP purposes. Have it reviewed by qualified legal counsel
            before production launch.
          </p>
        </GlassCard>
      </main>
      <SiteFooter />
    </>
  );
}
