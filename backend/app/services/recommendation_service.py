from __future__ import annotations
from datetime import date, timedelta
from typing import Dict, List, Optional, Set
from sqlalchemy.orm import Session

from app.services.outfit_service import OutfitService
from app.schemas.recommendation import DayPlan, WeeklyPlanResponse, WEEKDAYS

# Number of candidate outfits requested per day. A larger pool gives the
# variety filter (seen_top_ids / seen_bottom_ids) more fallback options
# to find a non-repeating combination before settling for the top score.
CANDIDATES_PER_DAY = 15


class RecommendationService:

    def __init__(self, db: Session) -> None:
        self.outfit_service = OutfitService(db)

    def generate_weekly_plan(
        self,
        user_id: int,
        default_occasion: str,
        season: str,
        day_overrides: Optional[Dict[str, str]] = None,
        start_date: Optional[date] = None,
    ) -> WeeklyPlanResponse:
        day_overrides = day_overrides or {}
        today = date.today()
        if start_date is None:
            days_until_monday = (7 - today.weekday()) % 7 or 7
            start_date = today + timedelta(days=days_until_monday)

        days: List[DayPlan] = []
        seen_top_ids: Set[int] = set()
        seen_bottom_ids: Set[int] = set()
        previous_day_items: Set[int] = set()   # consecutive-day repetition penalty
        complete = 0

        for i, day_name in enumerate(WEEKDAYS):
            day_date = start_date + timedelta(days=i)
            occasion = day_overrides.get(day_name, default_occasion)

            try:
                outfits = self.outfit_service.generate_outfits(
                    user_id, occasion, season,
                    count=CANDIDATES_PER_DAY,
                    extra_recently_worn_ids=previous_day_items,
                )
            except Exception:
                days.append(DayPlan(
                    day=day_name,
                    date=day_date,
                    outfit=None,
                    occasion=occasion,
                    note="Not enough wardrobe items for this day.",
                ))
                previous_day_items = set()
                continue

            def positions_of(outfit):
                top_id = next((oi.clothing_item_id for oi in outfit.items if oi.position == "top"), None)
                bottom_id = next((oi.clothing_item_id for oi in outfit.items if oi.position == "bottom"), None)
                return top_id, bottom_id

            # Tiered selection — each tier is a hard filter, falling back only
            # if no candidate in the pool satisfies it:
            #   1. Introduces a top/bottom not used anywhere this week AND
            #      doesn't repeat yesterday's top/bottom (best variety).
            #   2. Doesn't repeat yesterday's top/bottom (consecutive-day
            #      requirement — "important requirement" per spec).
            #   3. Best-scored candidate overall (last resort — small wardrobe).
            chosen = None
            for outfit in outfits:
                top_id, bottom_id = positions_of(outfit)
                no_consecutive_repeat = top_id not in previous_day_items and bottom_id not in previous_day_items
                introduces_new = top_id not in seen_top_ids and bottom_id not in seen_bottom_ids
                if no_consecutive_repeat and introduces_new:
                    chosen = outfit
                    break

            if chosen is None:
                for outfit in outfits:
                    top_id, bottom_id = positions_of(outfit)
                    if top_id not in previous_day_items and bottom_id not in previous_day_items:
                        chosen = outfit
                        break

            if chosen is None:
                chosen = outfits[0]   # last resort: best score even if it repeats yesterday

            top_id = next((oi.clothing_item_id for oi in chosen.items if oi.position == "top"), None)
            bottom_id = next((oi.clothing_item_id for oi in chosen.items if oi.position == "bottom"), None)

            if top_id:
                seen_top_ids.add(top_id)
            if bottom_id:
                seen_bottom_ids.add(bottom_id)

            previous_day_items = {iid for iid in (top_id, bottom_id) if iid is not None}

            from app.schemas.outfit import OutfitResponse
            days.append(DayPlan(
                day=day_name,
                date=day_date,
                outfit=OutfitResponse.from_orm_with_scores(chosen),
                occasion=occasion,
                score=chosen.total_score,
            ))
            complete += 1

        return WeeklyPlanResponse(
            week_start=start_date,
            season=season,
            days=days,
            total_unique_tops=len(seen_top_ids),
            total_unique_bottoms=len(seen_bottom_ids),
            coverage=complete / 7,
        )
