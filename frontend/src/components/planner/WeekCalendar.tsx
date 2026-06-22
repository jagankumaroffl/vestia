import { DayOutfit } from "./DayOutfit";
import { OCCASIONS, OCCASION_LABELS } from "@/types/outfit";
import type { WeeklyPlanResponse, Weekday } from "@/types/api";

interface WeekCalendarProps {
  plan: WeeklyPlanResponse;
  dayOverrides: Partial<Record<Weekday, string>>;
  defaultOccasion: string;
  onOverrideChange: (day: Weekday, occasion: string | null) => void;
}

const SELECT_CLASS =
  "bg-canvas border border-line rounded-card px-2 py-1 text-xs text-ink-muted appearance-none cursor-pointer hover:border-ink-faint focus:border-gold transition-colors";

export function WeekCalendar({ plan, dayOverrides, defaultOccasion, onOverrideChange }: WeekCalendarProps) {
  return (
    <div className="flex flex-col gap-6">
      <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-7 gap-3">
        {plan.days.map((day) => (
          <div key={day.day} className="flex flex-col gap-2">
            <select
              className={SELECT_CLASS}
              value={dayOverrides[day.day as Weekday] ?? ""}
              onChange={(e) => onOverrideChange(day.day as Weekday, e.target.value || null)}
            >
              <option value="">Default ({OCCASION_LABELS[defaultOccasion as keyof typeof OCCASION_LABELS] ?? defaultOccasion})</option>
              {OCCASIONS.map((o) => (
                <option key={o} value={o}>{OCCASION_LABELS[o]}</option>
              ))}
            </select>
            <DayOutfit day={day} />
          </div>
        ))}
      </div>
    </div>
  );
}
