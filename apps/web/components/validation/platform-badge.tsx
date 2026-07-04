import { PLATFORM_LABELS, type Platform } from "@rlr/shared";

interface PlatformBadgeProps {
  platform: Platform | string | null | undefined;
}

export function PlatformBadge({ platform }: PlatformBadgeProps) {
  const label =
    platform && platform in PLATFORM_LABELS
      ? PLATFORM_LABELS[platform as Platform]
      : platform
        ? String(platform)
        : "Generic CSV";

  return (
    <span className="inline-flex h-7 items-center rounded-full bg-secondary px-3 text-[0.72rem] font-medium uppercase tracking-[0.12em] text-muted-foreground">
      {label}
    </span>
  );
}
