import { create } from "zustand";
import { plannerApi } from "@/services/plannerApi";
import type { Weekday, WeeklyPlanResponse } from "@/types/api";
import type { Occasion } from "@/types/outfit";
import type { Season } from "@/types/clothing";

interface PlannerState {
  occasion: Occasion;
  season: Season;
  dayOverrides: Partial<Record<Weekday, string>>;
  plan: WeeklyPlanResponse | null;
  loading: boolean;
  error: string | null;

  setOccasion: (occasion: Occasion) => void;
  setSeason: (season: Season) => void;
  setDayOverride: (day: Weekday, occasion: string | null) => void;
  generatePlan: () => Promise<void>;
}

export const usePlannerStore = create<PlannerState>((set, get) => ({
  occasion: "casual",
  season: "all_season",
  dayOverrides: {},
  plan: null,
  loading: false,
  error: null,

  setOccasion: (occasion) => set({ occasion }),
  setSeason: (season) => set({ season }),

  setDayOverride: (day, occasion) => {
    const next = { ...get().dayOverrides };
    if (occasion === null) {
      delete next[day];
    } else {
      next[day] = occasion;
    }
    set({ dayOverrides: next });
  },

  generatePlan: async () => {
    const { occasion, season, dayOverrides } = get();
    set({ loading: true, error: null });
    try {
      const plan = await plannerApi.generateWeeklyPlan({
        occasion,
        season,
        day_overrides: Object.keys(dayOverrides).length ? dayOverrides : undefined,
      });
      set({ plan, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false, plan: null });
    }
  },
}));
