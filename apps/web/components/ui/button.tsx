import { cva, type VariantProps } from "class-variance-authority";
import { forwardRef, type ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const buttonVariants = cva(
  "inline-flex items-center justify-center font-medium transition-all duration-fast ease-out focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        primary: "bg-primary text-white hover:brightness-[1.02] active:bg-primary-active",
        secondary: "bg-white text-primary border border-gray-200 hover:border-gray-300",
        ghost: "bg-transparent text-gray-700 hover:bg-gray-100",
        danger: "bg-error text-white hover:brightness-[1.02]",
      },
      size: {
        sm: "h-10 px-4 text-small rounded-button",
        md: "h-12 px-6 text-body rounded-button",
        lg: "h-14 px-8 text-large rounded-button",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  },
);

export interface ButtonProps
  extends ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, ...props }, ref) => (
    <button ref={ref} className={cn(buttonVariants({ variant, size }), className)} {...props} />
  ),
);

Button.displayName = "Button";
