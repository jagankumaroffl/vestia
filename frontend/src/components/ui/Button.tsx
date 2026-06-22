import { forwardRef, type ButtonHTMLAttributes } from "react";
import { cn } from "@/utils/cn";

type Variant = "primary" | "outline" | "ghost" | "danger";
type Size = "sm" | "md";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantStyles: Record<Variant, string> = {
  primary:
    "bg-gold text-canvas border border-gold hover:bg-gold-glow hover:border-gold-glow disabled:bg-gold-dim disabled:border-gold-dim disabled:text-ink-faint",
  outline:
    "bg-transparent text-ink border border-line hover:border-ink-faint hover:bg-raised disabled:text-ink-faint disabled:border-line",
  ghost:
    "bg-transparent text-ink-muted border border-transparent hover:text-ink hover:bg-raised disabled:text-ink-faint",
  danger:
    "bg-transparent text-clay-light border border-clay-dim hover:bg-clay-dim/20 disabled:text-ink-faint disabled:border-line",
};

const sizeStyles: Record<Size, string> = {
  sm: "px-3 py-1.5 text-xs",
  md: "px-4 py-2.5 text-sm",
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "primary", size = "md", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "font-sans uppercase tracking-tag font-medium rounded-card transition-colors duration-150",
          "disabled:cursor-not-allowed",
          variantStyles[variant],
          sizeStyles[size],
          className
        )}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";
