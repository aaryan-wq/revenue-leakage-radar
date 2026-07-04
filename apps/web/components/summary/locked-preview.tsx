"use client";

import { Lock } from "lucide-react";
import { AnalyticsEvents } from "@rlr/shared";

import { Reveal, Stagger, StaggerItem } from "@/components/motion";
import { GlassCard } from "@/components/ui/glass-card";
import { captureEvent } from "@/lib/analytics/client";
import { getStoredAuditSession } from "@/lib/audit-session";
import { formatCurrency, type LockedPreviewItem } from "@rlr/shared";
import { PRODUCT_NAMES } from "@/lib/pricing-content";

interface LockedPreviewProps {
  items: LockedPreviewItem[];
}

export function LockedPreview({ items }: LockedPreviewProps) {
  if (items.length === 0) return null;

  return (
    <section className="border-t border-line pt-12">
      <Reveal>
        <div className="flex items-center gap-3">
          <Lock className="h-5 w-5 text-muted-foreground" strokeWidth={1.75} />
          <h3 className="font-heading text-2xl tracking-tight text-foreground">
            Detailed findings preview
          </h3>
        </div>
        <p className="mt-3 max-w-xl text-sm leading-relaxed text-muted-foreground">
          Unlock the {PRODUCT_NAMES.verificationReport} to view customer names, invoice evidence,
          and remediation steps.
        </p>
      </Reveal>

      <Stagger className="mt-10 grid gap-4 md:grid-cols-3">
        {items.map((item, index) => (
          <StaggerItem key={`${item.category}-${index}`}>
            <GlassCard
              padding="sm"
              subtle
              className="relative cursor-pointer overflow-hidden"
              onClick={() => {
                const session = getStoredAuditSession();
                captureEvent(AnalyticsEvents.FINDING_PREVIEW_EXPANDED, {
                  audit_id: session?.auditId,
                  category: item.category,
                  title: item.title,
                });
              }}
            >
              <div className="select-none blur-sm">
                <p className="text-sm font-medium text-foreground">{item.title}</p>
                <p className="mt-2 text-sm text-muted-foreground">{item.category_label}</p>
                <p className="mt-4 font-heading text-xl tracking-tight tnum">
                  {formatCurrency(item.arr)}
                </p>
                <p className="mt-4 text-sm text-muted-foreground">Customer names hidden</p>
                <p className="text-sm text-muted-foreground">Invoice evidence hidden</p>
              </div>
              <div className="absolute inset-0 flex items-center justify-center bg-card/70 backdrop-blur-sm">
                <Lock className="h-6 w-6 text-muted-foreground" strokeWidth={1.75} />
              </div>
            </GlassCard>
          </StaggerItem>
        ))}
      </Stagger>
    </section>
  );
}
