"use client";

import { Search } from "lucide-react";
import { CATEGORIES, STYLES, SEASONS } from "@/types/clothing";
import { titleCase } from "@/utils/colorUtils";
import { useWardrobeStore } from "@/store/wardrobeStore";

const SELECT_CLASS =
  "bg-surface border border-line rounded-card px-3 py-2 text-sm text-ink appearance-none cursor-pointer hover:border-ink-faint focus:border-gold transition-colors";

export function FilterBar() {
  const { filters, setFilters, searchQuery, setSearchQuery } = useWardrobeStore();

  return (
    <div className="flex flex-col sm:flex-row gap-3 px-6 md:px-10 py-4 border-b border-line bg-surface/40">
      <div className="relative flex-1 min-w-[180px]">
        <Search
          size={15}
          className="absolute left-3 top-1/2 -translate-y-1/2 text-ink-muted pointer-events-none"
        />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search wardrobe…"
          className="w-full bg-surface border border-line rounded-card pl-9 pr-3 py-2 text-sm text-ink placeholder:text-ink-faint focus:border-gold transition-colors"
        />
      </div>

      <select
        className={SELECT_CLASS}
        value={filters.category ?? ""}
        onChange={(e) => setFilters({ ...filters, category: (e.target.value || undefined) as any })}
      >
        <option value="">All Categories</option>
        {CATEGORIES.map((c) => (
          <option key={c} value={c}>{titleCase(c)}</option>
        ))}
      </select>

      <select
        className={SELECT_CLASS}
        value={filters.style ?? ""}
        onChange={(e) => setFilters({ ...filters, style: (e.target.value || undefined) as any })}
      >
        <option value="">All Styles</option>
        {STYLES.map((s) => (
          <option key={s} value={s}>{titleCase(s)}</option>
        ))}
      </select>

      <select
        className={SELECT_CLASS}
        value={filters.season ?? ""}
        onChange={(e) => setFilters({ ...filters, season: (e.target.value || undefined) as any })}
      >
        <option value="">All Seasons</option>
        {SEASONS.map((s) => (
          <option key={s} value={s}>{titleCase(s)}</option>
        ))}
      </select>
    </div>
  );
}
