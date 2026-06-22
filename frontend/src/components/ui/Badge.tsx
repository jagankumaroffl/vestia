import { type HTMLAttributes } from "react";
import { cn } from "@/utils/cn";

type Tone = "neutral" | "gold" | "sage" | "clay";

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone;
}

const toneStyles: Record<Tone, string> = {
  neutral: "border-line text-ink-muted",
  gold: "border-gold-dim text-gold",
  sage: "border-sage-dim text-sage-light",
  clay: "border-clay-dim text-clay-light",
};

export function Badge({ className, tone = "neutral", ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 px-2 py-0.5 rounded-card border font-mono text-[0.625rem] uppercase tracking-tag",
        toneStyles[tone],
        className
      )}
      {...props}
    />
  );
}
