from __future__ import annotations
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


# ── Enums as literals ────────────────────────────────────────────────────────

CATEGORIES = ["topwear", "bottomwear", "footwear", "accessory", "outerwear"]
PATTERNS = ["solid", "striped", "checked", "printed", "floral", "graphic", "textured"]
STYLES = ["casual", "formal", "business_casual", "smart_casual", "party", "sports", "ethnic"]
SEASONS = ["summer", "winter", "rainy", "all_season"]
GENDERS = ["male", "female", "unisex"]


# ── Request Schemas ───────────────────────────────────────────────────────────

class ClothingItemCreate(BaseModel):
    category: str = Field(..., description="topwear | bottomwear | footwear | accessory | outerwear")
    subcategory: str = Field(..., description="e.g. t-shirt, jeans, oxford shirt")
    primary_color: str
    secondary_color: Optional[str] = None
    pattern: str = Field(default="solid")
    style: str = Field(..., description="casual | formal | business_casual | smart_casual | party")
    season: str = Field(default="all_season")
    gender: str = Field(default="unisex")
    tags: List[str] = Field(default_factory=list)


class ClothingItemUpdate(BaseModel):
    """All fields optional — patch semantics."""
    category: Optional[str] = None
    subcategory: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    pattern: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    gender: Optional[str] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


# ── Response Schemas ──────────────────────────────────────────────────────────

class ClothingItemResponse(BaseModel):
    id: int
    user_id: int
    image_path: str
    category: str
    subcategory: str
    primary_color: str
    secondary_color: Optional[str]
    pattern: str
    style: str
    season: str
    gender: str
    tags: List[str]
    is_active: bool
    wear_count: int
    last_worn: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ClothingItemSummary(BaseModel):
    """Lightweight version used inside outfit responses."""
    id: int
    category: str
    subcategory: str
    primary_color: str
    style: str
    image_path: str

    class Config:
        from_attributes = True


class WardrobeFilterParams(BaseModel):
    category: Optional[str] = None
    style: Optional[str] = None
    season: Optional[str] = None
    color: Optional[str] = None
    pattern: Optional[str] = None
    is_active: bool = True
