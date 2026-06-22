from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.config import settings
from app.services.statistics_service import StatisticsService
from app.schemas.recommendation import WardrobeStatsResponse

router = APIRouter()


@router.get("/statistics", response_model=WardrobeStatsResponse)
def get_statistics(
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    return StatisticsService(db).get_stats(user_id)
