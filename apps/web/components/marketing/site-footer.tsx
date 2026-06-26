import Link from "next/link";

const SUPPORT_EMAIL =
  process.env.SUPPORT_EMAIL ?? process.env.NEXT_PUBLIC_SUPPORT_EMAIL ?? "support@revenueleakageradar.com";

export function SiteFooter() {
  return (
    <footer className="border-t border-border">
      <div className="mx-auto max-w-container px-8 py-16">
        <div className="grid gap-10 md:grid-cols-3">
          <div>
            <p className="text-h4 font-semibold text-primary">Revenue Leakage Radar</p>
            <p className="mt-3 text-body text-gray-500">
              Deterministic revenue verification for finance teams.
            </p>
          </div>
          <div>
            <p className="text-overline uppercase text-gray-500">Product</p>
            <ul className="mt-4 space-y-2 text-body">
              <li>
                <Link href="/upload" className="text-gray-600 underline-offset-4 hover:text-gray-900 hover:underline">
                  Run Free Scan
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="text-gray-600 underline-offset-4 hover:text-gray-900 hover:underline">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/security" className="text-gray-600 underline-offset-4 hover:text-gray-900 hover:underline">
                  Security
                </Link>
              </li>
            </ul>
          </div>
          <div>
            <p className="text-overline uppercase text-gray-500">Support</p>
            <ul className="mt-4 space-y-2 text-body">
              <li>
                <Link href="/faq" className="text-gray-600 underline-offset-4 hover:text-gray-900 hover:underline">
                  FAQ
                </Link>
              </li>
              <li>
                <Link href="/contact" className="text-gray-600 underline-offset-4 hover:text-gray-900 hover:underline">
                  Contact
                </Link>
              </li>
              <li>
                <a href={`mailto:${SUPPORT_EMAIL}`} className="text-gray-600 underline-offset-4 hover:text-gray-900 hover:underline">
                  {SUPPORT_EMAIL}
                </a>
              </li>
            </ul>
          </div>
        </div>
        <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-border pt-8 text-small text-gray-400">
          <p>© {new Date().getFullYear()} Revenue Leakage Radar</p>
          <div className="flex gap-6">
            <Link href="/privacy" className="hover:text-gray-600 hover:underline">
              Privacy
            </Link>
            <Link href="/terms" className="hover:text-gray-600 hover:underline">
              Terms
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
