from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.schemas.clothing import ClothingItemSummary


# ── Outfit Item ───────────────────────────────────────────────────────────────

class OutfitItemResponse(BaseModel):
    id: int
    position: str                       # top | bottom | shoes | outerwear | accessory
    clothing_item: ClothingItemSummary

    class Config:
        from_attributes = True


# ── Outfit Scores ─────────────────────────────────────────────────────────────

class OutfitScores(BaseModel):
    total_score: float = Field(..., ge=0.0, le=1.0)
    color_score: float = Field(..., ge=0.0, le=1.0)
    style_score: float = Field(..., ge=0.0, le=1.0)
    occasion_score: float = Field(..., ge=0.0, le=1.0)
    season_score: float = Field(..., ge=0.0, le=1.0)
    repetition_score: float = Field(..., ge=0.0, le=1.0)


# ── Request Schemas ───────────────────────────────────────────────────────────

class GenerateOutfitRequest(BaseModel):
    occasion: str = Field(
        ...,
        description="casual | college | office | business_meeting | formal_event | party | date_night | wedding | travel"
    )
    season: str = Field(
        ...,
        description="summer | winter | rainy | all_season"
    )
    count: int = Field(default=3, ge=1, le=10, description="Number of outfit options to return")


class MarkOutfitWornRequest(BaseModel):
    outfit_id: int
    worn_date: Optional[datetime] = None
    occasion: Optional[str] = None
    notes: Optional[str] = None


# ── Response Schemas ──────────────────────────────────────────────────────────

class OutfitResponse(BaseModel):
    id: int
    user_id: int
    name: Optional[str]
    occasion: str
    season: str
    scores: OutfitScores
    items: List[OutfitItemResponse]
    created_at: datetime

    class Config:
        from_attributes = True

    @classmethod
    def from_orm_with_scores(cls, outfit) -> "OutfitResponse":
        return cls(
            id=outfit.id,
            user_id=outfit.user_id,
            name=outfit.name,
            occasion=outfit.occasion,
            season=outfit.season,
            scores=OutfitScores(
                total_score=outfit.total_score,
                color_score=outfit.color_score,
                style_score=outfit.style_score,
                occasion_score=outfit.occasion_score,
                season_score=outfit.season_score,
                repetition_score=outfit.repetition_score,
            ),
            items=[
                OutfitItemResponse(
                    id=oi.id,
                    position=oi.position,
                    clothing_item=ClothingItemSummary.model_validate(oi.clothing_item),
                )
                for oi in outfit.items
            ],
            created_at=outfit.created_at,
        )
