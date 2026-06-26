"use client";

import { useEffect } from "react";
import { usePathname } from "next/navigation";
import Lenis from "lenis";
import { Toaster } from "sonner";

const SMOOTH_SCROLL_PATHS = ["/", "/pricing", "/security", "/faq", "/contact", "/summary", "/report"];

function shouldUseLenis(pathname: string): boolean {
  if (SMOOTH_SCROLL_PATHS.includes(pathname)) return true;
  if (pathname.startsWith("/report/")) return true;
  return false;
}

export function AppProviders({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  useEffect(() => {
    if (!shouldUseLenis(pathname)) return;

    const prefersReduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReduced) return;

    const lenis = new Lenis({ duration: 1.2, smoothWheel: true });
    let frame: number;

    function raf(time: number) {
      lenis.raf(time);
      frame = requestAnimationFrame(raf);
    }

    frame = requestAnimationFrame(raf);
    document.documentElement.classList.add("lenis", "lenis-smooth");

    return () => {
      cancelAnimationFrame(frame);
      lenis.destroy();
      document.documentElement.classList.remove("lenis", "lenis-smooth");
    };
  }, [pathname]);

  return (
    <>
      {children}
      <Toaster position="top-right" richColors closeButton duration={4000} />
    </>
  );
}
