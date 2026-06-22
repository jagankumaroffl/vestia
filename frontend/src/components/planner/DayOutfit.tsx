"use client";

import { useState } from "react";
import Image from "next/image";
import { Shirt } from "lucide-react";
import { ScoreDial } from "@/components/ui/ScoreDial";
import { Badge } from "@/components/ui/Badge";
import { thumbnailUrl } from "@/services/api";
import { formatShortDate } from "@/utils/formatters";
import { titleCase } from "@/utils/colorUtils";
import { OCCASION_LABELS, type Occasion } from "@/types/outfit";
import type { DayPlan } from "@/types/api";

const POSITION_ORDER = ["top", "outerwear", "bottom", "shoes", "accessory"];

export function DayOutfit({ day }: { day: DayPlan }) {
  const items = day.outfit
    ? [...day.outfit.items].sort(
        (a, b) => POSITION_ORDER.indexOf(a.position) - POSITION_ORDER.indexOf(b.position)
      )
    : [];

  return (
    <div className="flex flex-col bg-surface border border-line rounded-card overflow-hidden">
      <div className="px-3 py-2.5 border-b border-line flex items-center justify-between">
        <div>
          <p className="text-sm text-ink">{day.day}</p>
          {day.date && <p className="eyebrow">{formatShortDate(day.date)}</p>}
        </div>
        {day.outfit && <ScoreDial score={day.score} size={40} />}
      </div>

      <div className="px-3 py-2">
        <Badge tone="sage">{OCCASION_LABELS[day.occasion as Occasion] ?? titleCase(day.occasion)}</Badge>
      </div>

      {day.outfit ? (
        <div className="grid grid-cols-2 gap-1.5 p-3 pt-1">
          {items.map((oi) => (
            <div key={oi.id} className="relative aspect-square bg-raised border border-line rounded-card overflow-hidden">
              <ItemImage path={oi.clothing_item.image_path} />
            </div>
          ))}
        </div>
      ) : (
        <div className="px-3 pb-3 pt-1">
          <p className="text-xs text-ink-faint">{day.note || "No outfit available."}</p>
        </div>
      )}
    </div>
  );
}

function ItemImage({ path }: { path: string }) {
  const [error, setError] = useState(false);
  if (error) {
    return (
      <div className="absolute inset-0 flex items-center justify-center text-ink-faint">
        <Shirt size={16} strokeWidth={1} />
      </div>
    );
  }
  return (
    <Image
      src={thumbnailUrl(path)}
      alt=""
      fill
      sizes="120px"
      className="object-cover"
      onError={() => setError(true)}
      unoptimized
    />
  );
}
