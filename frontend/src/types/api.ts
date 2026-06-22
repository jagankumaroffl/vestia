import type { Outfit } from "./outfit";

export const WEEKDAYS = [
  "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
] as const;

export type Weekday = typeof WEEKDAYS[number];

export interface DayPlan {
  day: Weekday;
  date: string | null;
  outfit: Outfit | null;
  occasion: string;
  score: number;
  note?: string | null;
}

export interface WeeklyPlanRequest {
  occasion: string;
  season: string;
  day_overrides?: Partial<Record<Weekday, string>>;
  start_date?: string;
}

export interface WeeklyPlanResponse {
  week_start: string | null;
  season: string;
  days: DayPlan[];
  total_unique_tops: number;
  total_unique_bottoms: number;
  coverage: number;
}

export interface UploadAnalysisResult {
  clothing_item_id: number;
  image_path: string;
  category: string;
  subcategory: string;
  primary_color: string;
  secondary_color: string | null;
  pattern: string;
  style: string;
  season: string;
  gender: string;
  confidence: number;
  needs_review: boolean;
}

export interface WardrobeStats {
  total_items: number;
  active_items: number;
  category_breakdown: Record<string, number>;
  color_breakdown: Record<string, number>;
  style_breakdown: Record<string, number>;
  season_breakdown: Record<string, number>;
  most_worn: { id: number; subcategory: string; wear_count: number }[];
  least_worn: { id: number; subcategory: string; wear_count: number }[];
  total_outfits_generated: number;
  total_outfits_worn: number;
}
