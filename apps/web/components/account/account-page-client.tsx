"use client";

import { useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { UserProfile } from "@clerk/nextjs";
import { useAppAuth } from "@/lib/app-auth";

import { LegalLinks } from "@/components/legal/legal-links";
import { Reveal } from "@/components/motion";
import { Button } from "@/components/ui/button";
import { HairlineCard } from "@/components/ui/hairline-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { useWorkspaceDashboard } from "@/lib/hooks/use-workspace-dashboard";

const WORKSPACE_PAGE_CLASS = "mx-auto max-w-marketing space-y-12 px-6 py-12 md:px-10";

export function AccountPageClient() {
  const router = useRouter();
  const { isSignedIn, isLoaded } = useAppAuth();
  const { dashboard, isLoading, error, reload } = useWorkspaceDashboard();

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/account");
    }
  }, [isLoaded, isSignedIn, router]);

  if (!isLoaded || (isLoading && !dashboard)) {
    return <PageLoadingSkeleton message="Loading account…" variant="default" />;
  }

  if (error && !dashboard) {
    return (
      <div className={WORKSPACE_PAGE_CLASS}>
        <HairlineCard padding="md" className="border-destructive/20 bg-destructive/5 text-center">
          <p className="text-muted-foreground">{error}</p>
          <Button className="mt-6" onClick={() => void reload()}>
            Retry
          </Button>
        </HairlineCard>
      </div>
    );
  }

  return (
    <div className={WORKSPACE_PAGE_CLASS}>
      <Reveal>
        <div>
          <p className="text-[0.72rem] uppercase tracking-[0.16em] text-muted-foreground">Workspace</p>
          <h1 className="mt-2 font-heading text-3xl tracking-tight">Settings</h1>
          <p className="mt-2 text-muted-foreground">
            Manage your profile, security, and account preferences.
          </p>
        </div>
      </Reveal>

      <Reveal delay={0.05}>
        <HairlineCard padding="md">
          <h2 className="font-heading text-2xl tracking-tight">Account Overview</h2>
          <div className="mt-6 grid gap-6 sm:grid-cols-2">
            <div>
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">Company</p>
              <p className="mt-2 text-foreground">{dashboard?.company_name ?? "-"}</p>
            </div>
            <div>
              <p className="text-[0.72rem] uppercase tracking-[0.14em] text-muted-foreground">
                Reports Remaining
              </p>
              <p className="mt-2 font-heading text-2xl tracking-tight tnum">
                {dashboard?.reports_remaining ?? 0}
              </p>
            </div>
          </div>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link href="/dashboard">
              <Button variant="secondary" size="sm">
                Dashboard
              </Button>
            </Link>
            <Link href="/billing">
              <Button variant="secondary" size="sm">
                Billing
              </Button>
            </Link>
          </div>
        </HairlineCard>
      </Reveal>

      <Reveal delay={0.1}>
        <HairlineCard padding="md">
          <h2 className="font-heading text-2xl tracking-tight">Profile &amp; Security</h2>
          <p className="mt-2 text-sm text-muted-foreground">
            Manage your email, password, and connected accounts.
          </p>
          <div className="mt-8">
            <UserProfile routing="hash" />
          </div>
        </HairlineCard>
      </Reveal>

      <Reveal delay={0.15}>
        <div className="space-y-4">
          <LegalLinks />
          <p className="text-sm text-muted-foreground">
            To delete your account, use the account management options above or contact{" "}
            <a href="mailto:contact@paevo.co" className="text-primary hover:underline">
              contact@paevo.co
            </a>
            .
          </p>
        </div>
      </Reveal>
    </div>
  );
}
