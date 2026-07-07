import Link from "next/link";

import { LegalLinks } from "@/components/legal/legal-links";

export function WorkspaceLegalFooter() {
  return (
    <footer className="border-t border-line/60">
      <div className="mx-auto flex max-w-marketing flex-col gap-3 px-6 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between md:px-10">
        <span>© {new Date().getFullYear()} Paevo</span>
        <nav className="flex flex-wrap items-center gap-x-4 gap-y-1" aria-label="Support and legal">
          <Link href="/contact" className="transition-colors hover:text-foreground">
            Contact
          </Link>
          <Link href="/feedback" className="transition-colors hover:text-foreground">
            Feedback
          </Link>
          <LegalLinks linkClassName="text-xs" />
        </nav>
      </div>
    </footer>
  );
}
