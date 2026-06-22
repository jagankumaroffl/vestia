from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.config import settings
from app.services.outfit_service import OutfitService
from app.schemas.outfit import GenerateOutfitRequest, MarkOutfitWornRequest, OutfitResponse

router = APIRouter()


@router.post("/generate-outfit", response_model=List[OutfitResponse], status_code=201)
def generate_outfit(
    body: GenerateOutfitRequest,
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    outfits = OutfitService(db).generate_outfits(
        user_id, body.occasion, body.season, body.count
    )
    return [OutfitResponse.from_orm_with_scores(o) for o in outfits]


@router.get("/outfits", response_model=List[OutfitResponse])
def list_outfits(
    occasion: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    outfits = OutfitService(db).list_outfits(user_id, occasion=occasion, season=season, skip=skip, limit=limit)
    return [OutfitResponse.from_orm_with_scores(o) for o in outfits]


@router.get("/outfits/{outfit_id}", response_model=OutfitResponse)
def get_outfit(
    outfit_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return OutfitResponse.from_orm_with_scores(OutfitService(db).get_outfit(outfit_id))


@router.post("/outfits/{outfit_id}/worn", status_code=204)
def mark_outfit_worn(
    body: MarkOutfitWornRequest,
    outfit_id: int = Path(..., gt=0),
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    OutfitService(db).mark_worn(
        user_id, outfit_id, body.worn_date, body.occasion, body.notes
    )


@router.delete("/outfits/{outfit_id}", status_code=204)
def delete_outfit(
    outfit_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    OutfitService(db).delete_outfit(outfit_id)
