"use client";

import { useEffect, useRef } from "react";
import { usePathname } from "next/navigation";

import { exitAuditFromFunnel } from "@/lib/audit-session";

const AUDIT_PATH_PREFIXES = ["/upload", "/validation", "/analysis", "/summary"] as const;

function isAuditPath(pathname: string): boolean {
  return AUDIT_PATH_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
}

export function AuditSessionLifecycle() {
  const pathname = usePathname();
  const previousPathRef = useRef(pathname);

  useEffect(() => {
    const previousPath = previousPathRef.current;
    previousPathRef.current = pathname;

    if (isAuditPath(previousPath) && !isAuditPath(pathname)) {
      void exitAuditFromFunnel(previousPath);
    }
  }, [pathname]);

  return null;
}
