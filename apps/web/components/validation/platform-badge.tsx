import { PLATFORM_LABELS, type Platform } from "@rlr/shared";

interface PlatformBadgeProps {
  platform: Platform | string | null | undefined;
}

export function PlatformBadge({ platform }: PlatformBadgeProps) {
  if (!platform) return null;

  const label =
    platform in PLATFORM_LABELS
      ? PLATFORM_LABELS[platform as Platform]
      : platform;

  return (
    <span className="inline-flex h-7 items-center rounded-full bg-gray-100 px-3 text-caption font-medium text-gray-700">
      {label}
    </span>
  );
}
