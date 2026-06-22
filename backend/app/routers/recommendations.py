from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.config import settings
from app.services.outfit_service import OutfitService
from app.schemas.outfit import OutfitResponse

router = APIRouter()


@router.get("/recommendations", response_model=List[OutfitResponse])
def get_recommendations(
    occasion: str = Query(..., description="Occasion to recommend for"),
    season: str = Query(..., description="Current season"),
    count: int = Query(default=5, ge=1, le=10),
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    """Generate top-N outfit recommendations for a given occasion and season."""
    outfits = OutfitService(db).generate_outfits(user_id, occasion, season, count)
    return [OutfitResponse.from_orm_with_scores(o) for o in outfits]
