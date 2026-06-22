"use client";

import { useState } from "react";
import Image from "next/image";
import { Shirt } from "lucide-react";
import { Modal } from "@/components/ui/Modal";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { ColorSwatch } from "@/components/ui/ColorSwatch";
import { thumbnailUrl } from "@/services/api";
import { titleCase } from "@/utils/colorUtils";
import { pluralize, formatShortDate } from "@/utils/formatters";
import { CATEGORIES, STYLES, SEASONS, type ClothingItem, type ClothingItemUpdate } from "@/types/clothing";
import { useWardrobeStore } from "@/store/wardrobeStore";

interface ClothingDetailModalProps {
  item: ClothingItem | null;
  onClose: () => void;
}

const FIELD_CLASS =
  "w-full bg-canvas border border-line rounded-card px-3 py-2 text-sm text-ink focus:border-gold transition-colors";

export function ClothingDetailModal({ item, onClose }: ClothingDetailModalProps) {
  const { updateItem, removeItem } = useWardrobeStore();
  const [imgError, setImgError] = useState(false);
  const [saving, setSaving] = useState(false);
  const [draft, setDraft] = useState<ClothingItemUpdate>({});

  if (!item) return null;

  const current = { ...item, ...draft };
  const dirty = Object.keys(draft).length > 0;

  const handleSave = async () => {
    setSaving(true);
    try {
      await updateItem(item.id, draft);
      setDraft({});
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    await removeItem(item.id);
    onClose();
  };

  return (
    <Modal open={!!item} onClose={onClose} title={titleCase(item.subcategory)}>
      <div className="grid sm:grid-cols-2 gap-5">
        <div className="relative aspect-square bg-raised rounded-card overflow-hidden">
          {!imgError ? (
            <Image
              src={thumbnailUrl(item.image_path)}
              alt={item.subcategory}
              fill
              className="object-cover"
              onError={() => setImgError(true)}
              unoptimized
            />
          ) : (
            <div className="absolute inset-0 flex items-center justify-center text-ink-faint">
              <Shirt size={40} strokeWidth={1} />
            </div>
          )}
        </div>

        <div className="flex flex-col gap-4">
          <div>
            <label className="eyebrow block mb-1.5">Category</label>
            <select
              className={FIELD_CLASS}
              value={current.category}
              onChange={(e) => setDraft({ ...draft, category: e.target.value as any })}
            >
              {CATEGORIES.map((c) => (
                <option key={c} value={c}>{titleCase(c)}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="eyebrow block mb-1.5">Style</label>
            <select
              className={FIELD_CLASS}
              value={current.style}
              onChange={(e) => setDraft({ ...draft, style: e.target.value as any })}
            >
              {STYLES.map((s) => (
                <option key={s} value={s}>{titleCase(s)}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="eyebrow block mb-1.5">Season</label>
            <select
              className={FIELD_CLASS}
              value={current.season}
              onChange={(e) => setDraft({ ...draft, season: e.target.value as any })}
            >
              {SEASONS.map((s) => (
                <option key={s} value={s}>{titleCase(s)}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="eyebrow block mb-1.5">Colors</label>
            <div className="flex items-center gap-2">
              <ColorSwatch name={current.primary_color || "grey"} size={18} />
              <span className="text-sm text-ink">{titleCase(current.primary_color || "")}</span>
              {current.secondary_color && (
                <>
                  <span className="text-ink-faint">/</span>
                  <ColorSwatch name={current.secondary_color} size={18} />
                  <span className="text-sm text-ink">{titleCase(current.secondary_color)}</span>
                </>
              )}
            </div>
          </div>

          <div className="flex flex-wrap gap-1.5">
            <Badge>{titleCase(item.pattern)}</Badge>
            <Badge tone="sage">{titleCase(item.gender)}</Badge>
            <Badge tone="gold">{pluralize(item.wear_count, "wear")}</Badge>
          </div>

          {item.last_worn && (
            <p className="eyebrow">Last worn {formatShortDate(item.last_worn)}</p>
          )}
        </div>
      </div>

      <div className="flex items-center justify-between mt-6 pt-4 border-t border-line">
        <Button variant="danger" size="sm" onClick={handleDelete}>
          Remove Item
        </Button>
        <Button variant="primary" size="sm" disabled={!dirty || saving} onClick={handleSave}>
          {saving ? "Saving…" : "Save Changes"}
        </Button>
      </div>
    </Modal>
  );
}
