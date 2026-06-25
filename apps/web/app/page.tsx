import Link from "next/link";
import { ArrowRight, Shield, Upload, Zap } from "lucide-react";

export default function HomePage() {
  return (
    <>
      <section className="border-b border-gray-100 bg-white">
        <div className="mx-auto max-w-container px-8 py-24">
          <div className="mx-auto max-w-reading text-center">
            <h1 className="text-display text-primary">
              Find recoverable revenue in your billing data
            </h1>
            <p className="mt-6 text-large text-gray-500">
              Upload billing CSVs and receive a free Revenue Verification Summary in minutes.
              Deterministic checks. CFO-grade evidence.
            </p>
            <div className="mt-10 flex items-center justify-center gap-4">
              <Link
                href="/upload"
                className="inline-flex h-14 items-center gap-2 rounded-button bg-primary px-8 text-large font-medium text-white transition-all duration-fast hover:brightness-[1.02]"
              >
                Run Free Revenue Scan
                <ArrowRight className="h-5 w-5" strokeWidth={1.75} />
              </Link>
              <Link
                href="/pricing"
                className="inline-flex h-14 items-center rounded-button border border-gray-200 bg-white px-8 text-large font-medium text-primary transition-colors hover:border-gray-300"
              >
                View Pricing
              </Link>
            </div>
            <p className="mt-6 text-caption text-gray-400">
              No account required · Stripe, Chargebee, Maxio, Zuora exports supported
            </p>
          </div>
        </div>
      </section>

      <section className="mx-auto max-w-container px-8 py-24">
        <h2 className="text-center text-h2 text-primary">How it works</h2>
        <div className="mt-16 grid gap-8 md:grid-cols-3">
          {[
            {
              icon: Upload,
              title: "Upload CSVs",
              description: "Export billing data from your platform and upload five required files.",
            },
            {
              icon: Zap,
              title: "Revenue Verification",
              description: "Deterministic rules scan subscriptions, invoices, and pricing for leakage.",
            },
            {
              icon: Shield,
              title: "Recover Revenue",
              description: "Get evidence-backed findings with estimated ARR impact and remediation steps.",
            },
          ].map((step) => (
            <div
              key={step.title}
              className="rounded-card border border-gray-100 bg-white p-8 shadow-card transition-all duration-normal hover:-translate-y-0.5 hover:shadow-card-hover"
            >
              <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gray-50">
                <step.icon className="h-6 w-6 text-primary" strokeWidth={1.75} />
              </div>
              <h3 className="mt-6 text-h4 text-gray-900">{step.title}</h3>
              <p className="mt-3 text-body text-gray-500">{step.description}</p>
            </div>
          ))}
        </div>
      </section>
    </>
  );
}
