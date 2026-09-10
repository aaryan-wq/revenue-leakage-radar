"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect, useId, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Menu, X } from "lucide-react";

import { Logo, NAV_LOGO_CLASS } from "@/components/brand/logo";
import { MarketingAuthActions } from "@/components/marketing-auth-actions";
import { cn } from "@/lib/utils";

const links = [
  { href: "/", label: "Overview" },
  { href: "/saas-revenue-leakage-calculator", label: "Calculator" },
  { href: "/demo", label: "Demo" },
  { href: "/how-it-works", label: "How It Works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/security", label: "Security" },
  { href: "/faq", label: "FAQ" },
  { href: "/feedback", label: "Feedback" },
];

function isLinkActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname.startsWith(href);
}

export function MarketingNav() {
  const pathname = usePathname();
  const [menuOpen, setMenuOpen] = useState(false);
  const menuId = useId();

  useEffect(() => {
    setMenuOpen(false);
  }, [pathname]);

  useEffect(() => {
    if (!menuOpen) return;

    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setMenuOpen(false);
    };
    window.addEventListener("keydown", onKeyDown);

    return () => {
      document.body.style.overflow = previousOverflow;
      window.removeEventListener("keydown", onKeyDown);
    };
  }, [menuOpen]);

  useEffect(() => {
    const media = window.matchMedia("(min-width: 768px)");
    const onChange = () => {
      if (media.matches) setMenuOpen(false);
    };
    media.addEventListener("change", onChange);
    return () => media.removeEventListener("change", onChange);
  }, []);

  return (
    <header className="sticky top-0 z-50">
      <div className="absolute inset-0 -z-10 bg-background/70 backdrop-blur-xl" />
      <nav
        className={cn(
          "relative mx-auto flex h-[72px] max-w-marketing items-center justify-between gap-4 px-6 md:px-10",
        )}
      >
        <Logo variant="full" priority className={cn("hidden shrink-0 sm:block", NAV_LOGO_CLASS.full)} />
        <Logo variant="short" priority className={cn("shrink-0 sm:hidden", NAV_LOGO_CLASS.short)} />

        <div className="pointer-events-none absolute left-1/2 top-1/2 hidden -translate-x-1/2 -translate-y-1/2 md:block">
          <div className="pointer-events-auto flex items-center gap-0.5 whitespace-nowrap">
            {links.map((link) => {
              const active = isLinkActive(pathname, link.href);
              return (
                <Link
                  key={link.href}
                  href={link.href}
                  className="relative px-3 py-2 text-[0.8rem] tracking-wide text-muted-foreground transition-colors hover:text-foreground"
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
        </div>

        <div className="flex shrink-0 items-center gap-1 sm:gap-2">
          <MarketingAuthActions className="shrink-0 items-center" />
          <button
            type="button"
            className="inline-flex h-11 w-11 items-center justify-center rounded-full text-foreground transition-colors hover:bg-secondary md:hidden"
            aria-label={menuOpen ? "Close menu" : "Open menu"}
            aria-expanded={menuOpen}
            aria-controls={menuId}
            onClick={() => setMenuOpen((open) => !open)}
          >
            {menuOpen ? <X className="h-5 w-5" strokeWidth={1.75} /> : <Menu className="h-5 w-5" strokeWidth={1.75} />}
          </button>
        </div>
      </nav>

      <AnimatePresence>
        {menuOpen && (
          <motion.div
            id={menuId}
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.28, ease: [0.16, 1, 0.3, 1] }}
            className="overflow-hidden border-t border-line/60 md:hidden"
          >
            <div className="max-h-[calc(100dvh-72px)] overflow-y-auto bg-background/95 px-6 pb-8 pt-4 backdrop-blur-xl">
              <ul className="space-y-1">
                {links.map((link, index) => {
                  const active = isLinkActive(pathname, link.href);
                  return (
                    <motion.li
                      key={link.href}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{
                        duration: 0.28,
                        delay: 0.04 + index * 0.03,
                        ease: [0.16, 1, 0.3, 1],
                      }}
                    >
                      <Link
                        href={link.href}
                        onClick={() => setMenuOpen(false)}
                        className={cn(
                          "flex min-h-[44px] items-center rounded-xl px-4 text-[0.95rem] tracking-wide transition-colors",
                          active
                            ? "bg-secondary text-foreground"
                            : "text-muted-foreground hover:bg-secondary/60 hover:text-foreground",
                        )}
                      >
                        {link.label}
                      </Link>
                    </motion.li>
                  );
                })}
              </ul>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
