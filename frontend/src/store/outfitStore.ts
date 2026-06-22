import { create } from "zustand";
import { outfitApi } from "@/services/outfitApi";
import type { Occasion, Outfit } from "@/types/outfit";
import type { Season } from "@/types/clothing";

interface OutfitState {
  occasion: Occasion;
  season: Season;
  count: number;
  results: Outfit[];
  loading: boolean;
  error: string | null;

  setOccasion: (occasion: Occasion) => void;
  setSeason: (season: Season) => void;
  setCount: (count: number) => void;
  generate: () => Promise<void>;
  markWorn: (outfitId: number) => Promise<void>;
}

export const useOutfitStore = create<OutfitState>((set, get) => ({
  occasion: "casual",
  season: "all_season",
  count: 3,
  results: [],
  loading: false,
  error: null,

  setOccasion: (occasion) => set({ occasion }),
  setSeason: (season) => set({ season }),
  setCount: (count) => set({ count }),

  generate: async () => {
    const { occasion, season, count } = get();
    set({ loading: true, error: null });
    try {
      const results = await outfitApi.generate({ occasion, season, count });
      set({ results, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false, results: [] });
    }
  },

  markWorn: async (outfitId) => {
    await outfitApi.markWorn(outfitId);
  },
}));
