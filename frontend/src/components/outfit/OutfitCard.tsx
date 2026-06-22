"use client";

import { useState } from "react";
import Image from "next/image";
import { Shirt, Check } from "lucide-react";
import { Card, CardBody, CardFooter } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { Button } from "@/components/ui/Button";
import { ScoreDial } from "@/components/ui/ScoreDial";
import { ScoreDisplay } from "./ScoreDisplay";
import { thumbnailUrl } from "@/services/api";
import { titleCase } from "@/utils/colorUtils";
import { OCCASION_LABELS, POSITION_LABELS, type Outfit } from "@/types/outfit";

interface OutfitCardProps {
  outfit: Outfit;
  onMarkWorn?: (outfitId: number) => Promise<void>;
}

const POSITION_ORDER = ["top", "outerwear", "bottom", "shoes", "accessory"];

export function OutfitCard({ outfit, onMarkWorn }: OutfitCardProps) {
  const [marking, setMarking] = useState(false);
  const [worn, setWorn] = useState(false);

  const items = [...outfit.items].sort(
    (a, b) => POSITION_ORDER.indexOf(a.position) - POSITION_ORDER.indexOf(b.position)
  );

  const handleMarkWorn = async () => {
    if (!onMarkWorn) return;
    setMarking(true);
    try {
      await onMarkWorn(outfit.id);
      setWorn(true);
    } finally {
      setMarking(false);
    }
  };

  return (
    <Card>
      <CardBody>
        <div className="flex items-start justify-between gap-4 mb-4">
          <div>
            <Badge tone="sage">{OCCASION_LABELS[outfit.occasion]}</Badge>
            <p className="eyebrow mt-1.5">{titleCase(outfit.season)}</p>
          </div>
          <ScoreDial score={outfit.scores.total_score} label="Total" />
        </div>

        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-4">
          {items.map((oi) => (
            <div key={oi.id} className="flex flex-col gap-1.5">
              <div className="relative aspect-square bg-raised border border-line rounded-card overflow-hidden">
                <ImageOrFallback path={oi.clothing_item.image_path} />
              </div>
              <div>
                <p className="eyebrow">{POSITION_LABELS[oi.position]}</p>
                <p className="text-xs text-ink truncate">{titleCase(oi.clothing_item.subcategory)}</p>
              </div>
            </div>
          ))}
        </div>

        <ScoreDisplay scores={outfit.scores} />
      </CardBody>

      {onMarkWorn && (
        <CardFooter className="flex justify-end">
          <Button
            size="sm"
            variant={worn ? "ghost" : "outline"}
            onClick={handleMarkWorn}
            disabled={marking || worn}
          >
            {worn ? (
              <span className="flex items-center gap-1.5"><Check size={13} /> Marked Worn</span>
            ) : marking ? "Saving…" : "Mark as Worn Today"}
          </Button>
        </CardFooter>
      )}
    </Card>
  );
}

function ImageOrFallback({ path }: { path: string }) {
  const [error, setError] = useState(false);
  if (error) {
    return (
      <div className="absolute inset-0 flex items-center justify-center text-ink-faint">
        <Shirt size={20} strokeWidth={1} />
      </div>
    );
  }
  return (
    <Image
      src={thumbnailUrl(path)}
      alt=""
      fill
      sizes="160px"
      className="object-cover"
      onError={() => setError(true)}
      unoptimized
    />
  );
}
