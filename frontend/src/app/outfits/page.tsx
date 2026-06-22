"use client";

import { PageHeader } from "@/components/layout/PageHeader";
import { Button } from "@/components/ui/Button";
import { OccasionPicker } from "@/components/outfit/OccasionPicker";
import { OutfitCard } from "@/components/outfit/OutfitCard";
import { useOutfitStore } from "@/store/outfitStore";
import { Sparkles } from "lucide-react";

export default function OutfitsPage() {
  const {
    occasion, season, count, results, loading, error,
    setOccasion, setSeason, setCount, generate, markWorn,
  } = useOutfitStore();

  return (
    <div>
      <PageHeader
        eyebrow="Style Engine"
        title="Outfit Generator"
        description="Rule-based combinations scored on color harmony, style, occasion fit, season, and wardrobe variety."
      />

      <div className="px-6 md:px-10 py-6 border-b border-line">
        <div className="flex flex-col sm:flex-row sm:items-end gap-3 max-w-2xl">
          <div className="flex-1">
            <OccasionPicker
              occasion={occasion}
              season={season}
              onOccasionChange={setOccasion}
              onSeasonChange={setSeason}
            />
          </div>
          <div className="w-28">
            <label className="eyebrow block mb-1.5">Options</label>
            <select
              className="w-full bg-surface border border-line rounded-card px-3 py-2 text-sm text-ink appearance-none cursor-pointer hover:border-ink-faint focus:border-gold transition-colors"
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
            >
              {[1, 2, 3, 5].map((n) => (
                <option key={n} value={n}>{n}</option>
              ))}
            </select>
          </div>
          <Button onClick={generate} disabled={loading} className="sm:w-auto">
            <span className="flex items-center gap-2">
              <Sparkles size={14} />
              {loading ? "Generating…" : "Generate"}
            </span>
          </Button>
        </div>
      </div>

      <div className="px-6 md:px-10 py-8">
        {error && <p className="text-clay-light text-sm mb-4">{error}</p>}

        {results.length === 0 && !loading && !error && (
          <div className="text-center py-16 flex flex-col items-center gap-2">
            <Sparkles size={28} strokeWidth={1} className="text-ink-faint" />
            <p className="text-sm text-ink-muted">Choose an occasion and season, then generate outfits.</p>
          </div>
        )}

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-5">
          {results.map((outfit) => (
            <OutfitCard key={outfit.id} outfit={outfit} onMarkWorn={markWorn} />
          ))}
        </div>
      </div>
    </div>
  );
}
