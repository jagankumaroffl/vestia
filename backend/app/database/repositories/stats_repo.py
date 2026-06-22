from __future__ import annotations
from collections import Counter
from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database.models import ClothingItem, WardrobeStatistic, OutfitHistory


class StatsRepository:
    """
    All aggregate queries for wardrobe statistics.
    Results are cached in wardrobe_statistics table
    and refreshed on every mutation that triggers update_stats().
    """

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Read ──────────────────────────────────────────────────────────────────

    def get(self, user_id: int) -> Optional[WardrobeStatistic]:
        return (
            self.db.query(WardrobeStatistic)
            .filter(WardrobeStatistic.user_id == user_id)
            .first()
        )

    # ── Live aggregation ──────────────────────────────────────────────────────

    def compute_and_upsert(self, user_id: int) -> WardrobeStatistic:
        """
        Compute fresh statistics from raw tables and upsert into
        wardrobe_statistics. Called after upload or item deletion.
        """
        items: List[ClothingItem] = (
            self.db.query(ClothingItem)
            .filter(ClothingItem.user_id == user_id, ClothingItem.is_active == True)
            .all()
        )

        total = len(items)
        cat_breakdown  = dict(Counter(i.category      for i in items))
        color_breakdown = dict(Counter(i.primary_color for i in items))

        worn = [i for i in items if i.wear_count > 0]
        most_worn = [
            {"id": i.id, "subcategory": i.subcategory, "wear_count": i.wear_count}
            for i in sorted(worn, key=lambda x: x.wear_count, reverse=True)[:5]
        ]
        least_worn = [
            {"id": i.id, "subcategory": i.subcategory, "wear_count": i.wear_count}
            for i in sorted(worn, key=lambda x: x.wear_count)[:5]
        ]

        row = self.get(user_id)
        if row is None:
            row = WardrobeStatistic(user_id=user_id)
            self.db.add(row)

        row.total_items      = total
        row.category_breakdown = cat_breakdown
        row.color_breakdown    = color_breakdown
        row.most_worn_items    = most_worn
        row.least_worn_items   = least_worn
        row.updated_at         = datetime.now(timezone.utc)

        self.db.commit()
        self.db.refresh(row)
        return row

    # ── Convenience queries ───────────────────────────────────────────────────

    def count_by_category(self, user_id: int) -> dict:
        rows = (
            self.db.query(ClothingItem.category, func.count(ClothingItem.id))
            .filter(ClothingItem.user_id == user_id, ClothingItem.is_active == True)
            .group_by(ClothingItem.category)
            .all()
        )
        return {cat: cnt for cat, cnt in rows}

    def count_by_style(self, user_id: int) -> dict:
        rows = (
            self.db.query(ClothingItem.style, func.count(ClothingItem.id))
            .filter(ClothingItem.user_id == user_id, ClothingItem.is_active == True)
            .group_by(ClothingItem.style)
            .all()
        )
        return {style: cnt for style, cnt in rows}

    def count_by_season(self, user_id: int) -> dict:
        rows = (
            self.db.query(ClothingItem.season, func.count(ClothingItem.id))
            .filter(ClothingItem.user_id == user_id, ClothingItem.is_active == True)
            .group_by(ClothingItem.season)
            .all()
        )
        return {season: cnt for season, cnt in rows}

    def total_worn_events(self, user_id: int) -> int:
        return (
            self.db.query(func.count(OutfitHistory.id))
            .filter(OutfitHistory.user_id == user_id)
            .scalar() or 0
        )
