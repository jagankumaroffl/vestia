from __future__ import annotations
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.config import settings
from app.services.recommendation_service import RecommendationService
from app.schemas.recommendation import WeeklyPlanRequest, WeeklyPlanResponse

router = APIRouter()


@router.post("/weekly-plan", response_model=WeeklyPlanResponse)
def generate_weekly_plan(
    body: WeeklyPlanRequest,
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    """
    Generate a 7-day outfit plan avoiding consecutive repetition.
    Accepts per-day occasion overrides via day_overrides dict.
    """
    service = RecommendationService(db)
    return service.generate_weekly_plan(
        user_id,
        default_occasion=body.occasion,
        season=body.season,
        day_overrides=body.day_overrides,
        start_date=body.start_date,
    )
