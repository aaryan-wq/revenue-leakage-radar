"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { motion } from "framer-motion";

import { MarketingAuthActions } from "@/components/marketing-auth-actions";

const links = [
  { href: "/", label: "Overview" },
  { href: "/how-it-works", label: "How It Works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/security", label: "Security" },
  { href: "/faq", label: "FAQ" },
];

function isLinkActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function MarketingNav() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50">
      <div className="absolute inset-0 -z-10 bg-background/70 backdrop-blur-xl" />
      <nav className="mx-auto flex h-[72px] max-w-marketing items-center justify-between gap-4 px-6 md:px-10">
        <Link href="/" className="group flex shrink-0 items-center gap-2.5">
          <span className="relative flex h-2.5 w-2.5 items-center justify-center">
            <motion.span
              className="absolute inset-0 rounded-full bg-primary"
              animate={{ scale: [1, 1.9, 1], opacity: [0.5, 0, 0.5] }}
              transition={{ duration: 3.4, repeat: Infinity, ease: "easeInOut" }}
            />
            <span className="h-2.5 w-2.5 rounded-full bg-primary" />
          </span>
          <span className="font-heading text-[1.05rem] tracking-tight text-foreground">Radar</span>
        </Link>

        <div className="hidden items-center gap-0.5 md:flex">
          {links.map((link) => {
            const active = isLinkActive(pathname, link.href);
            return (
              <Link
                key={link.href}
                href={link.href}
                className="relative px-3.5 py-2 text-[0.8rem] tracking-wide text-muted-foreground transition-colors hover:text-foreground"
              >
                {active && (
                  <motion.span
                    layoutId="marketing-nav-pill"
                    className="absolute inset-0 rounded-full bg-secondary"
                    transition={{ type: "spring", stiffness: 380, damping: 32 }}
                  />
                )}
                <span className={active ? "relative text-foreground" : "relative"}>
                  {link.label}
                </span>
              </Link>
            );
          })}
        </div>

        <MarketingAuthActions />
      </nav>
    </header>
  );
}
