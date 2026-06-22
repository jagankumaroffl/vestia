import { OCCASIONS, OCCASION_LABELS, type Occasion } from "@/types/outfit";
import { SEASONS, type Season } from "@/types/clothing";
import { titleCase } from "@/utils/colorUtils";

const SELECT_CLASS =
  "bg-surface border border-line rounded-card px-3 py-2 text-sm text-ink appearance-none cursor-pointer hover:border-ink-faint focus:border-gold transition-colors";

interface OccasionPickerProps {
  occasion: Occasion;
  season: Season;
  onOccasionChange: (occasion: Occasion) => void;
  onSeasonChange: (season: Season) => void;
}

export function OccasionPicker({ occasion, season, onOccasionChange, onSeasonChange }: OccasionPickerProps) {
  return (
    <div className="flex flex-col sm:flex-row gap-3">
      <div className="flex-1">
        <label className="eyebrow block mb-1.5">Occasion</label>
        <select
          className={`${SELECT_CLASS} w-full`}
          value={occasion}
          onChange={(e) => onOccasionChange(e.target.value as Occasion)}
        >
          {OCCASIONS.map((o) => (
            <option key={o} value={o}>{OCCASION_LABELS[o]}</option>
          ))}
        </select>
      </div>
      <div className="flex-1">
        <label className="eyebrow block mb-1.5">Season</label>
        <select
          className={`${SELECT_CLASS} w-full`}
          value={season}
          onChange={(e) => onSeasonChange(e.target.value as Season)}
        >
          {SEASONS.map((s) => (
            <option key={s} value={s}>{titleCase(s)}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
