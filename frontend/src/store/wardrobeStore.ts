import { create } from "zustand";
import { wardrobeApi } from "@/services/wardrobeApi";
import type { ClothingItem, ClothingItemUpdate, WardrobeFilters } from "@/types/clothing";

interface WardrobeState {
  items: ClothingItem[];
  filters: WardrobeFilters;
  searchQuery: string;
  loading: boolean;
  error: string | null;

  setFilters: (filters: WardrobeFilters) => void;
  setSearchQuery: (query: string) => void;
  fetchItems: () => Promise<void>;
  updateItem: (id: number, updates: ClothingItemUpdate) => Promise<void>;
  removeItem: (id: number) => Promise<void>;

  /** Items after applying the local search query on top of server-side filters. */
  filteredItems: () => ClothingItem[];
}

export const useWardrobeStore = create<WardrobeState>((set, get) => ({
  items: [],
  filters: {},
  searchQuery: "",
  loading: false,
  error: null,

  setFilters: (filters) => {
    set({ filters });
    get().fetchItems();
  },

  setSearchQuery: (query) => set({ searchQuery: query }),

  fetchItems: async () => {
    set({ loading: true, error: null });
    try {
      const items = await wardrobeApi.list(get().filters);
      set({ items, loading: false });
    } catch (err) {
      set({ error: (err as Error).message, loading: false });
    }
  },

  updateItem: async (id, updates) => {
    const updated = await wardrobeApi.update(id, updates);
    set({ items: get().items.map((i) => (i.id === id ? updated : i)) });
  },

  removeItem: async (id) => {
    await wardrobeApi.remove(id);
    set({ items: get().items.filter((i) => i.id !== id) });
  },

  filteredItems: () => {
    const { items, searchQuery } = get();
    if (!searchQuery.trim()) return items;
    const q = searchQuery.trim().toLowerCase();
    return items.filter((item) =>
      [item.subcategory, item.primary_color, item.secondary_color, item.style, item.category]
        .filter(Boolean)
        .some((field) => (field as string).toLowerCase().includes(q))
    );
  },
}));
