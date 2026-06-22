import type { ClothingItemSummary } from "./clothing";

export type OutfitPosition = "top" | "bottom" | "shoes" | "outerwear" | "accessory";

export type Occasion =
  | "casual" | "college" | "office" | "business_meeting"
  | "formal_event" | "party" | "date_night" | "wedding" | "travel";

export interface OutfitScores {
  total_score: number;
  color_score: number;
  style_score: number;
  occasion_score: number;
  season_score: number;
  repetition_score: number;
}

export interface OutfitItem {
  id: number;
  position: OutfitPosition;
  clothing_item: ClothingItemSummary;
}

export interface Outfit {
  id: number;
  user_id: number;
  name: string | null;
  occasion: Occasion;
  season: string;
  scores: OutfitScores;
  items: OutfitItem[];
  created_at: string;
}

export interface GenerateOutfitRequest {
  occasion: Occasion;
  season: string;
  count?: number;
}

export interface MarkOutfitWornRequest {
  outfit_id: number;
  worn_date?: string;
  occasion?: string;
  notes?: string;
}

export const OCCASIONS: Occasion[] = [
  "casual", "college", "office", "business_meeting",
  "formal_event", "party", "date_night", "wedding", "travel",
];

export const OCCASION_LABELS: Record<Occasion, string> = {
  casual: "Casual",
  college: "College",
  office: "Office",
  business_meeting: "Business Meeting",
  formal_event: "Formal Event",
  party: "Party",
  date_night: "Date Night",
  wedding: "Wedding",
  travel: "Travel",
};

export const POSITION_LABELS: Record<OutfitPosition, string> = {
  top: "Top",
  bottom: "Bottom",
  shoes: "Shoes",
  outerwear: "Outerwear",
  accessory: "Accessory",
};
