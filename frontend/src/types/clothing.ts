export type ClothingCategory = "topwear" | "bottomwear" | "footwear" | "accessory" | "outerwear";

export type ClothingPattern =
  | "solid" | "striped" | "checked" | "printed" | "floral" | "graphic" | "textured";

export type ClothingStyle =
  | "casual" | "formal" | "business_casual" | "smart_casual" | "party" | "sports" | "ethnic";

export type Season = "summer" | "winter" | "rainy" | "all_season";

export type Gender = "male" | "female" | "unisex";

export interface ClothingItem {
  id: number;
  user_id: number;
  image_path: string;
  category: ClothingCategory;
  subcategory: string;
  primary_color: string;
  secondary_color: string | null;
  pattern: ClothingPattern;
  style: ClothingStyle;
  season: Season;
  gender: Gender;
  tags: string[];
  is_active: boolean;
  wear_count: number;
  last_worn: string | null;
  created_at: string;
}

export interface ClothingItemSummary {
  id: number;
  category: ClothingCategory;
  subcategory: string;
  primary_color: string;
  style: ClothingStyle;
  image_path: string;
}

export interface ClothingItemUpdate {
  category?: ClothingCategory;
  subcategory?: string;
  primary_color?: string;
  secondary_color?: string | null;
  pattern?: ClothingPattern;
  style?: ClothingStyle;
  season?: Season;
  gender?: Gender;
  tags?: string[];
  is_active?: boolean;
}

export interface WardrobeFilters {
  category?: ClothingCategory;
  style?: ClothingStyle;
  season?: Season;
  color?: string;
  pattern?: ClothingPattern;
}

export const CATEGORIES: ClothingCategory[] = [
  "topwear", "bottomwear", "footwear", "outerwear", "accessory",
];

export const STYLES: ClothingStyle[] = [
  "casual", "formal", "business_casual", "smart_casual", "party", "sports", "ethnic",
];

export const SEASONS: Season[] = ["summer", "winter", "rainy", "all_season"];

export const PATTERNS: ClothingPattern[] = [
  "solid", "striped", "checked", "printed", "floral", "graphic", "textured",
];
