"use client";

import { useState } from "react";
import Image from "next/image";
import { Shirt, Trash2 } from "lucide-react";
import { thumbnailUrl } from "@/services/api";
import { Badge } from "@/components/ui/Badge";
import { ColorSwatch } from "@/components/ui/ColorSwatch";
import { titleCase } from "@/utils/colorUtils";
import { pluralize } from "@/utils/formatters";
import type { ClothingItem } from "@/types/clothing";

interface ClothingCardProps {
  item: ClothingItem;
  onClick?: () => void;
  onDelete?: () => void;
}

export function ClothingCard({ item, onClick, onDelete }: ClothingCardProps) {
  const [imgError, setImgError] = useState(false);

  return (
    <div
      onClick={onClick}
      className="group bg-surface border border-line rounded-card overflow-hidden cursor-pointer hover:border-ink-faint transition-colors"
    >
      <div className="relative aspect-square bg-raised">
        {!imgError ? (
          <Image
            src={thumbnailUrl(item.image_path)}
            alt={item.subcategory}
            fill
            sizes="(max-width: 768px) 50vw, 220px"
            className="object-cover"
            onError={() => setImgError(true)}
            unoptimized
          />
        ) : (
          <div className="absolute inset-0 flex items-center justify-center text-ink-faint">
            <Shirt size={32} strokeWidth={1} />
          </div>
        )}

        {onDelete && (
          <button
            onClick={(e) => {
              e.stopPropagation();
              onDelete();
            }}
            aria-label="Delete item"
            className="absolute top-2 right-2 p-1.5 rounded-card bg-canvas/70 text-ink-muted opacity-0 group-hover:opacity-100 hover:text-clay-light transition-opacity"
          >
            <Trash2 size={14} />
          </button>
        )}

        <div className="absolute bottom-2 left-2 flex gap-1">
          <ColorSwatch name={item.primary_color} />
          {item.secondary_color && <ColorSwatch name={item.secondary_color} />}
        </div>
      </div>

      <div className="p-3">
        <p className="text-sm text-ink truncate">{titleCase(item.subcategory)}</p>
        <div className="flex items-center gap-1.5 mt-2 flex-wrap">
          <Badge tone="sage">{titleCase(item.category)}</Badge>
          <Badge>{titleCase(item.style)}</Badge>
        </div>
        <p className="eyebrow mt-2">{pluralize(item.wear_count, "wear")}</p>
      </div>
    </div>
  );
}
