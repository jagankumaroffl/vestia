import { formatScorePercent } from "@/utils/formatters";
import type { OutfitScores } from "@/types/outfit";

const SCORE_ROWS: { key: keyof OutfitScores; label: string; weight: string }[] = [
  { key: "color_score",      label: "Color",      weight: "35%" },
  { key: "style_score",      label: "Style",      weight: "30%" },
  { key: "occasion_score",   label: "Occasion",   weight: "20%" },
  { key: "season_score",     label: "Season",     weight: "10%" },
  { key: "repetition_score", label: "Variety",    weight: "5%"  },
];

export function ScoreDisplay({ scores }: { scores: OutfitScores }) {
  return (
    <div className="flex flex-col gap-2">
      {SCORE_ROWS.map(({ key, label, weight }) => (
        <div key={key} className="flex items-center gap-3">
          <span className="eyebrow w-20 shrink-0">{label}</span>
          <div className="flex-1 h-1 bg-line rounded-full overflow-hidden">
            <div
              className="h-full bg-gold"
              style={{ width: `${formatScorePercent(scores[key])}%` }}
            />
          </div>
          <span className="font-mono text-xs text-ink-muted w-8 text-right">
            {formatScorePercent(scores[key])}
          </span>
          <span className="font-mono text-[0.625rem] text-ink-faint w-8 text-right">
            {weight}
          </span>
        </div>
      ))}
    </div>
  );
}
