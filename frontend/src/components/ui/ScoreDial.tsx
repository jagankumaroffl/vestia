import { cn } from "@/utils/cn";

interface ScoreDialProps {
  /** Score from 0.0 to 1.0 */
  score: number;
  size?: number;
  label?: string;
  className?: string;
}

/**
 * Circular gauge styled after a tailor's measuring dial — a thin gold
 * arc tracing the score, with the percentage set in Cormorant Garamond.
 * This is Vestia's recurring "score" motif across cards, dashboard,
 * and the weekly planner.
 */
export function ScoreDial({ score, size = 64, label, className }: ScoreDialProps) {
  const pct = Math.max(0, Math.min(1, score));
  const radius = (size - 6) / 2;
  const circumference = 2 * Math.PI * radius;
  const offset = circumference * (1 - pct);
  const center = size / 2;

  return (
    <div className={cn("flex flex-col items-center gap-1.5", className)}>
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="-rotate-90">
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#2E2B28"
            strokeWidth={3}
          />
          <circle
            cx={center}
            cy={center}
            r={radius}
            fill="none"
            stroke="#C9A227"
            strokeWidth={3}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
            strokeLinecap="round"
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-display text-lg text-ink leading-none">
            {Math.round(pct * 100)}
          </span>
        </div>
      </div>
      {label && <span className="eyebrow">{label}</span>}
    </div>
  );
}
