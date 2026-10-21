import Image from "next/image";
import Link from "next/link";

import { cn } from "@/lib/utils";

type LogoVariant = "full" | "short";

type LogoProps = {
  variant?: LogoVariant;
  className?: string;
  href?: string | null;
  priority?: boolean;
};

/** Shared top row for every sticky nav. */
export const NAV_ROW_CLASS = "flex h-16 items-center";

export const NAV_LOGO_CLASS = {
  full: "h-7 w-auto sm:h-7",
  short: "h-7 w-7 sm:h-7 sm:w-7",
} as const;

/** Quiet label beside workspace actions. */
export const NAV_GREETING_CLASS = "hidden shrink-0 text-sm text-muted-foreground lg:block";

const LOGO_CONFIG: Record<
  LogoVariant,
  { src: string; width: number; height: number; alt: string; sizeClass: string }
> = {
  full: {
    src: "/brand/logo-full.png",
    width: 349,
    height: 102,
    alt: "Paevo",
    sizeClass: "h-10 w-auto sm:h-11",
  },
  short: {
    src: "/brand/logo-short.png",
    width: 101,
    height: 102,
    alt: "Paevo",
    sizeClass: "h-9 w-9 sm:h-10 sm:w-10",
  },
};

export function Logo({ variant = "full", className, href = "/", priority = false }: LogoProps) {
  const { src, width, height, alt, sizeClass } = LOGO_CONFIG[variant];

  const image = (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      priority={priority}
      className={cn("object-contain object-left", sizeClass, className)}
    />
  );

  if (href) {
    return (
      <Link href={href} className="inline-flex shrink-0 items-center" aria-label="Paevo home">
        {image}
      </Link>
    );
  }

  return image;
}
