"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { UserProfile } from "@clerk/nextjs";
import { useAppAuth } from "@/lib/app-auth";

import { Button } from "@/components/ui/button";
import { GlassCard } from "@/components/ui/glass-card";
import { PageLoadingSkeleton } from "@/components/ui/skeleton";
import { getDashboard } from "@/lib/report-api";
import { ApiError } from "@/lib/api";
import type { DashboardResponse } from "@rlr/shared";

export function AccountPageClient() {
  const router = useRouter();
  const { getToken, isSignedIn, isLoaded } = useAppAuth();
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadAccount = useCallback(async () => {
    if (!isSignedIn) return;
    try {
      const token = await getToken();
      if (!token) return;
      const data = await getDashboard(token);
      setDashboard(data);
      setError(null);
    } catch (err) {
      const message =
        err instanceof ApiError ? err.message : "Unable to load account information.";
      setError(message);
    } finally {
      setIsLoading(false);
    }
  }, [getToken, isSignedIn]);

  useEffect(() => {
    if (!isLoaded) return;
    if (!isSignedIn) {
      router.replace("/sign-in?redirect_url=/account");
      return;
    }
    void loadAccount();
  }, [isLoaded, isSignedIn, loadAccount, router]);

  if (!isLoaded || isLoading) {
    return <PageLoadingSkeleton message="Loading account…" />;
  }

  if (error && !dashboard) {
    return (
      <GlassCard padding="md" className="border-error/20 bg-error-bg text-center">
        <p className="text-body text-gray-700">{error}</p>
        <Button className="mt-6" onClick={() => void loadAccount()}>
          Retry
        </Button>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-16">
      <GlassCard padding="md">
        <h2 className="text-h3 font-semibold text-gray-900">Account Overview</h2>
        <div className="mt-6 grid gap-6 sm:grid-cols-2">
          <div>
            <p className="text-caption text-gray-500">Company</p>
            <p className="mt-2 text-body text-gray-900">
              {dashboard?.company_name ?? "—"}
            </p>
          </div>
          <div>
            <p className="text-caption text-gray-500">Reports Remaining</p>
            <p className="mt-2 text-h3 font-semibold tabular-nums text-gray-900">
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
      </GlassCard>

      <GlassCard padding="md">
        <h2 className="text-h3 font-semibold text-gray-900">Profile &amp; Security</h2>
        <p className="mt-2 text-body text-gray-500">
          Manage your email, password, and connected accounts.
        </p>
        <div className="mt-8">
          <UserProfile routing="hash" />
        </div>
      </GlassCard>

      <p className="text-small text-gray-500">
        To delete your account, use the account management options above or contact{" "}
        <a href="mailto:support@revenueleakageradar.com" className="text-primary hover:underline">
          support
        </a>
        .
      </p>
    </div>
  );
}
