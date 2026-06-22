from __future__ import annotations
from collections import Counter
from sqlalchemy.orm import Session

from app.database.repositories.clothing_repo import ClothingRepository
from app.database.repositories.outfit_repo import OutfitRepository
from app.database.repositories.history_repo import HistoryRepository
from app.schemas.recommendation import WardrobeStatsResponse


class StatisticsService:

    def __init__(self, db: Session) -> None:
        self.clothing_repo = ClothingRepository(db)
        self.outfit_repo = OutfitRepository(db)
        self.history_repo = HistoryRepository(db)

    def get_stats(self, user_id: int) -> WardrobeStatsResponse:
        all_items = self.clothing_repo.get_all(user_id, is_active=True, limit=1000)
        inactive = self.clothing_repo.get_all(user_id, is_active=False, limit=1000)

        cat_count = Counter(i.category for i in all_items)
        color_count = Counter(i.primary_color for i in all_items)
        style_count = Counter(i.style for i in all_items)
        season_count = Counter(i.season for i in all_items)

        # Most / least worn (exclude never-worn for least)
        worn = [i for i in all_items if i.wear_count > 0]
        most_worn = sorted(worn, key=lambda x: x.wear_count, reverse=True)[:5]
        least_worn = sorted(worn, key=lambda x: x.wear_count)[:5]

        return WardrobeStatsResponse(
            total_items=len(all_items) + len(inactive),
            active_items=len(all_items),
            category_breakdown=dict(cat_count),
            color_breakdown=dict(color_count),
            style_breakdown=dict(style_count),
            season_breakdown=dict(season_count),
            most_worn=[
                {"id": i.id, "subcategory": i.subcategory, "wear_count": i.wear_count}
                for i in most_worn
            ],
            least_worn=[
                {"id": i.id, "subcategory": i.subcategory, "wear_count": i.wear_count}
                for i in least_worn
            ],
            total_outfits_generated=self.outfit_repo.count(user_id),
            total_outfits_worn=self.history_repo.count_worn(user_id),
        )
