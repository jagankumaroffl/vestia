from __future__ import annotations
from datetime import date as date_type, datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from app.schemas.outfit import OutfitResponse


# ── Single Recommendation ─────────────────────────────────────────────────────

class RecommendationResponse(BaseModel):
    id: int
    outfit_id: int
    occasion: str
    season: str
    score: float
    recommended_date: Optional[datetime]
    is_accepted: bool
    outfit: OutfitResponse

    class Config:
        from_attributes = True


# ── Weekly Planner ────────────────────────────────────────────────────────────

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


class DayPlan(BaseModel):
    day: str                          # Monday … Sunday
    date: Optional[date_type] = None
    outfit: Optional[OutfitResponse] = None
    occasion: str
    score: float = 0.0
    note: Optional[str] = None        # e.g. "wardrobe too small for full week"


class WeeklyPlanRequest(BaseModel):
    occasion: str = Field(
        default="casual",
        description="Default occasion applied to all days unless overridden"
    )
    season: str = Field(
        default="all_season",
        description="Season context for the week"
    )
    day_overrides: Optional[Dict[str, str]] = Field(
        default=None,
        description="Per-day occasion override e.g. {'Friday': 'office', 'Saturday': 'casual'}"
    )
    start_date: Optional[date_type] = None   # Defaults to next Monday


class WeeklyPlanResponse(BaseModel):
    week_start: Optional[date_type]
    season: str
    days: List[DayPlan]
    total_unique_tops: int
    total_unique_bottoms: int
    coverage: float = Field(..., description="Fraction of days with a complete outfit (0-1)")


# ── Upload Analysis Result ────────────────────────────────────────────────────

class UploadAnalysisResult(BaseModel):
    """Returned immediately after image upload + CV analysis."""
    clothing_item_id: int
    image_path: str
    category: str
    subcategory: str
    primary_color: str
    secondary_color: Optional[str]
    pattern: str
    style: str
    season: str
    gender: str
    confidence: float = Field(..., ge=0.0, le=1.0, description="CV pipeline confidence score")
    needs_review: bool = Field(
        default=False,
        description="True when confidence < 0.6 — user should verify metadata"
    )


# ── Statistics ────────────────────────────────────────────────────────────────

class WardrobeStatsResponse(BaseModel):
    total_items: int
    active_items: int
    category_breakdown: Dict[str, int]
    color_breakdown: Dict[str, int]
    style_breakdown: Dict[str, int]
    season_breakdown: Dict[str, int]
    most_worn: List[Dict]
    least_worn: List[Dict]
    total_outfits_generated: int
    total_outfits_worn: int
