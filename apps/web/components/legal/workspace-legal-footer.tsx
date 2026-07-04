import { LegalLinks } from "@/components/legal/legal-links";

export function WorkspaceLegalFooter() {
  return (
    <footer className="border-t border-line/60">
      <div className="mx-auto flex max-w-marketing flex-col gap-3 px-6 py-6 text-xs text-muted-foreground sm:flex-row sm:items-center sm:justify-between md:px-10">
        <span>© {new Date().getFullYear()} Paevo</span>
        <LegalLinks />
      </div>
    </footer>
  );
}
