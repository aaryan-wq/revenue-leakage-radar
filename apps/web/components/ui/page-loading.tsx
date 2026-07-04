"use client";

import { AnimatePresence, motion } from "framer-motion";
import { type ReactNode } from "react";

import { glide } from "@/components/motion";
import { Skeleton } from "@/components/ui/skeleton";
import { useDelayedLoading, useDelayedMount } from "@/lib/hooks/use-delayed-loading";
import { staggerFast } from "@/lib/motion/variants";
import { useMotionEnabled } from "@/lib/motion/use-motion-enabled";
import { cn } from "@/lib/utils";

export type PageLoadingVariant =
  | "default"
  | "report"
  | "dashboard"
  | "list"
  | "detail";

interface PageLoadingStateProps {
  message: string;
  variant?: PageLoadingVariant;
  className?: string;
}

function LoadingProgressBar() {
  const motionEnabled = useMotionEnabled();

  if (!motionEnabled) {
    return (
      <div
        className="fixed inset-x-0 top-0 z-50 h-[2px] bg-primary/30"
        aria-hidden="true"
      />
    );
  }

  return (
    <div className="fixed inset-x-0 top-0 z-50 h-[2px] overflow-hidden bg-line" aria-hidden="true">
      <motion.div
        className="h-full w-1/3 bg-primary"
        initial={{ x: "-100%" }}
        animate={{ x: "400%" }}
        transition={{
          duration: 1.4,
          ease: [0.4, 0, 0.2, 1],
          repeat: Infinity,
          repeatDelay: 0.15,
        }}
      />
    </div>
  );
}

function SkeletonBlock({
  className,
  delay = 0,
}: {
  className?: string;
  delay?: number;
}) {
  const motionEnabled = useMotionEnabled();

  if (!motionEnabled) {
    return <Skeleton className={className} />;
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.45, ease: glide, delay }}
    >
      <Skeleton className={className} />
    </motion.div>
  );
}

function ReportSkeleton() {
  return (
    <div className="mx-auto max-w-report px-6 md:px-10">
      <SkeletonBlock className="h-3 w-48" />
      <SkeletonBlock className="mt-8 h-14 w-full max-w-2xl" delay={0.05} />
      <SkeletonBlock className="mt-6 h-5 w-full max-w-xl" delay={0.1} />
      <div className="mt-16 grid gap-10 border-t border-line pt-12 md:grid-cols-[1.3fr_1fr]">
        <div>
          <SkeletonBlock className="h-3 w-40" delay={0.15} />
          <SkeletonBlock className="mt-4 h-20 w-full max-w-md" delay={0.2} />
          <SkeletonBlock className="mt-5 h-4 w-full max-w-sm" delay={0.25} />
        </div>
        <div className="grid grid-cols-2 gap-px overflow-hidden rounded-xl border border-line bg-line">
          {Array.from({ length: 4 }).map((_, index) => (
            <div key={index} className="bg-card px-5 py-6">
              <SkeletonBlock className="h-3 w-16" delay={0.18 + index * 0.04} />
              <SkeletonBlock className="mt-3 h-8 w-20" delay={0.22 + index * 0.04} />
            </div>
          ))}
        </div>
      </div>
      <div className="mt-20 space-y-12">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="border-t border-line pt-10">
            <SkeletonBlock className="h-7 w-2/3 max-w-lg" delay={0.3 + index * 0.06} />
            <SkeletonBlock className="mt-4 h-4 w-full max-w-md" delay={0.34 + index * 0.06} />
            <SkeletonBlock className="mt-8 h-10 w-32" delay={0.38 + index * 0.06} />
          </div>
        ))}
      </div>
    </div>
  );
}

function DashboardSkeleton() {
  return (
    <div className="mx-auto max-w-marketing px-6 md:px-10">
      <SkeletonBlock className="h-3 w-36" />
      <SkeletonBlock className="mt-6 h-16 w-full max-w-xl" delay={0.05} />
      <div className="mt-12 grid gap-6 md:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="rounded-xl border border-line bg-card p-8">
            <SkeletonBlock className="h-3 w-24" delay={0.1 + index * 0.05} />
            <SkeletonBlock className="mt-4 h-10 w-32" delay={0.14 + index * 0.05} />
            <SkeletonBlock className="mt-2 h-4 w-28" delay={0.18 + index * 0.05} />
          </div>
        ))}
      </div>
      <div className="mt-10 grid gap-0 overflow-hidden rounded-xl border border-line lg:grid-cols-[20rem_1fr]">
        <div className="border-b border-line p-6 lg:border-b-0 lg:border-r">
          <SkeletonBlock className="h-3 w-28" delay={0.25} />
          <div className="mt-6 space-y-4">
            {Array.from({ length: 6 }).map((_, index) => (
              <SkeletonBlock
                key={index}
                className="h-12 w-full"
                delay={0.28 + index * 0.03}
              />
            ))}
          </div>
        </div>
        <div className="p-8 md:p-12">
          <SkeletonBlock className="h-3 w-20" delay={0.3} />
          <SkeletonBlock className="mt-6 h-12 w-full max-w-lg" delay={0.34} />
          <SkeletonBlock className="mt-10 h-24 w-full max-w-md" delay={0.38} />
        </div>
      </div>
    </div>
  );
}

function ListSkeleton() {
  return (
    <div className="mx-auto max-w-marketing px-6 md:px-10">
      <SkeletonBlock className="h-3 w-32" />
      <SkeletonBlock className="mt-6 h-12 w-full max-w-md" delay={0.05} />
      <SkeletonBlock className="mt-3 h-4 w-full max-w-sm" delay={0.1} />
      <div className="mt-12 space-y-4">
        {Array.from({ length: 5 }).map((_, index) => (
          <div
            key={index}
            className="flex items-center justify-between gap-4 rounded-xl border border-line p-6"
          >
            <div className="min-w-0 flex-1">
              <SkeletonBlock className="h-5 w-48" delay={0.14 + index * 0.04} />
              <SkeletonBlock className="mt-2 h-4 w-64" delay={0.18 + index * 0.04} />
            </div>
            <SkeletonBlock className="h-9 w-24 shrink-0 rounded-full" delay={0.2 + index * 0.04} />
          </div>
        ))}
      </div>
    </div>
  );
}

function DetailSkeleton() {
  return (
    <div className="mx-auto max-w-report px-6 py-16 md:px-10 md:py-20">
      <div className="flex flex-wrap gap-3">
        <SkeletonBlock className="h-3 w-16" />
        <SkeletonBlock className="h-3 w-20" delay={0.03} />
        <SkeletonBlock className="h-3 w-24" delay={0.06} />
      </div>
      <SkeletonBlock className="mt-8 h-12 w-full max-w-2xl" delay={0.1} />
      <div className="mt-10 flex flex-wrap gap-14 border-y border-line py-10">
        <SkeletonBlock className="h-20 w-48" delay={0.15} />
        <SkeletonBlock className="h-16 w-32" delay={0.2} />
        <SkeletonBlock className="h-16 w-24" delay={0.24} />
      </div>
      <div className="mt-10 grid gap-px overflow-hidden rounded-xl border border-line bg-line sm:grid-cols-3">
        {Array.from({ length: 3 }).map((_, index) => (
          <div key={index} className="bg-card px-5 py-6">
            <SkeletonBlock className="h-3 w-16" delay={0.28 + index * 0.04} />
            <SkeletonBlock className="mt-3 h-8 w-24" delay={0.32 + index * 0.04} />
          </div>
        ))}
      </div>
    </div>
  );
}

function DefaultSkeleton() {
  return (
    <div className="mx-auto max-w-marketing px-6 md:px-10">
      <SkeletonBlock className="h-3 w-40" />
      <SkeletonBlock className="mt-6 h-12 w-full max-w-lg" delay={0.05} />
      <SkeletonBlock className="mt-4 h-4 w-full max-w-md" delay={0.1} />
      <div className="mt-12 grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-line bg-card p-8">
          <SkeletonBlock className="h-3 w-24" delay={0.15} />
          <SkeletonBlock className="mt-4 h-10 w-36" delay={0.2} />
          <SkeletonBlock className="mt-2 h-4 w-28" delay={0.24} />
        </div>
        <div className="rounded-xl border border-line bg-card p-8">
          <SkeletonBlock className="h-3 w-28" delay={0.18} />
          <SkeletonBlock className="mt-4 h-10 w-32" delay={0.22} />
          <SkeletonBlock className="mt-2 h-4 w-32" delay={0.26} />
        </div>
      </div>
      <div className="mt-8 overflow-hidden rounded-xl border border-line bg-card p-6">
        <SkeletonBlock className="h-4 w-full max-w-md" delay={0.3} />
        <div className="mt-6 space-y-3">
          {Array.from({ length: 4 }).map((_, index) => (
            <SkeletonBlock
              key={index}
              className="h-12 w-full"
              delay={0.34 + index * 0.03}
            />
          ))}
        </div>
      </div>
    </div>
  );
}

function LoadingSkeletonLayout({ variant }: { variant: PageLoadingVariant }) {
  switch (variant) {
    case "report":
      return <ReportSkeleton />;
    case "dashboard":
      return <DashboardSkeleton />;
    case "list":
      return <ListSkeleton />;
    case "detail":
      return <DetailSkeleton />;
    default:
      return <DefaultSkeleton />;
  }
}

export function PageLoadingState({
  message,
  variant = "default",
  className,
}: PageLoadingStateProps) {
  const motionEnabled = useMotionEnabled();

  const content = (
    <div
      className={cn("relative min-h-[50vh] py-16 md:py-20", className)}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <LoadingProgressBar />
      <motion.p
        className="mx-auto mb-12 max-w-marketing px-6 text-center text-sm tracking-wide text-muted-foreground md:px-10"
        initial={motionEnabled ? { opacity: 0, y: 6 } : false}
        animate={motionEnabled ? { opacity: 1, y: 0 } : undefined}
        transition={{ duration: 0.5, ease: glide }}
      >
        <span className="sr-only">Loading: </span>
        {message}
      </motion.p>
      <motion.div
        initial={motionEnabled ? "hidden" : false}
        animate={motionEnabled ? "visible" : false}
        variants={staggerFast}
      >
        <LoadingSkeletonLayout variant={variant} />
      </motion.div>
    </div>
  );

  if (!motionEnabled) {
    return content;
  }

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0, transition: { duration: 0.3, ease: glide } }}
      transition={{ duration: 0.35, ease: glide }}
    >
      {content}
    </motion.div>
  );
}

interface PageShellProps {
  isLoading: boolean;
  message: string;
  variant?: PageLoadingVariant;
  children: ReactNode;
  className?: string;
}

export function PageShell({
  isLoading,
  message,
  variant = "default",
  children,
  className,
}: PageShellProps) {
  const motionEnabled = useMotionEnabled();
  const showLoading = useDelayedLoading(isLoading);
  const showContent = !isLoading && !showLoading;

  return (
    <AnimatePresence mode="wait">
      {showLoading ? (
        <PageLoadingState
          key="loading"
          message={message}
          variant={variant}
          className={className}
        />
      ) : showContent ? (
        <motion.div
          key="content"
          className={className}
          initial={motionEnabled ? { opacity: 0, y: 8 } : false}
          animate={motionEnabled ? { opacity: 1, y: 0 } : undefined}
          exit={motionEnabled ? { opacity: 0, transition: { duration: 0.15 } } : undefined}
          transition={{ duration: 0.35, ease: glide }}
        >
          {children}
        </motion.div>
      ) : null}
    </AnimatePresence>
  );
}

/** Early-return loader with delay. Prefer PageShell for smooth exit transitions. */
export function DelayedPageFallback({
  message,
  variant = "default",
}: {
  message: string;
  variant?: PageLoadingVariant;
}) {
  const visible = useDelayedMount();

  if (!visible) return null;

  return <PageLoadingState message={message} variant={variant} />;
}

/** @deprecated Use PageShell or DelayedPageFallback instead */
export function PageLoadingSkeleton({
  message,
  variant = "default",
}: {
  message: string;
  variant?: PageLoadingVariant;
}) {
  return <DelayedPageFallback message={message} variant={variant} />;
}
