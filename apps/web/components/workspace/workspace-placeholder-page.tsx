import Link from "next/link";
import type { LucideIcon } from "lucide-react";

import { Reveal } from "@/components/motion";
import { HairlineCard } from "@/components/ui/hairline-card";

interface WorkspacePlaceholderPageProps {
  title: string;
  description: string;
  items?: { title: string; body: string }[];
  links?: { href: string; label: string }[];
  icon?: LucideIcon;
}

export function WorkspacePlaceholderPage({
  title,
  description,
  items = [],
  links = [],
}: WorkspacePlaceholderPageProps) {
  return (
    <div className="mx-auto max-w-reading px-6 py-12 md:px-10">
      <Reveal>
        <h1 className="font-heading text-3xl tracking-tight">{title}</h1>
        <p className="mt-4 leading-relaxed text-muted-foreground">{description}</p>
      </Reveal>

      {items.length > 0 && (
        <div className="mt-10 space-y-4">
          {items.map((item) => (
            <HairlineCard key={item.title} padding="md">
              <h2 className="font-heading text-lg tracking-tight">{item.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">{item.body}</p>
            </HairlineCard>
          ))}
        </div>
      )}

      {links.length > 0 && (
        <Reveal delay={0.1} className="mt-10 flex flex-wrap gap-4">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="text-sm font-medium text-primary underline-offset-4 hover:underline"
            >
              {link.label} →
            </Link>
          ))}
        </Reveal>
      )}
    </div>
  );
}
