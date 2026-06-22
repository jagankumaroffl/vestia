"use client";

import { useEffect, useState } from "react";
import { Shirt } from "lucide-react";
import { ClothingCard } from "./ClothingCard";
import { ClothingDetailModal } from "./ClothingDetailModal";
import { useWardrobeStore } from "@/store/wardrobeStore";
import type { ClothingItem } from "@/types/clothing";

export function ClothingGrid() {
  const { loading, error, fetchItems, filteredItems, removeItem } = useWardrobeStore();
  const [selected, setSelected] = useState<ClothingItem | null>(null);

  useEffect(() => {
    fetchItems();
  }, [fetchItems]);

  const items = filteredItems();

  if (loading) {
    return (
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 px-6 md:px-10 py-6">
        {Array.from({ length: 10 }).map((_, i) => (
          <div key={i} className="aspect-square bg-surface border border-line rounded-card animate-pulse" />
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-6 md:px-10 py-12 text-center">
        <p className="text-clay-light text-sm">{error}</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="px-6 md:px-10 py-20 text-center flex flex-col items-center gap-3">
        <Shirt size={32} strokeWidth={1} className="text-ink-faint" />
        <p className="text-ink-muted text-sm">No items match these filters.</p>
        <p className="eyebrow">Upload clothing to build your wardrobe</p>
      </div>
    );
  }

  return (
    <>
      <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4 px-6 md:px-10 py-6">
        {items.map((item) => (
          <ClothingCard
            key={item.id}
            item={item}
            onClick={() => setSelected(item)}
            onDelete={() => removeItem(item.id)}
          />
        ))}
      </div>
      <ClothingDetailModal item={selected} onClose={() => setSelected(null)} />
    </>
  );
}
