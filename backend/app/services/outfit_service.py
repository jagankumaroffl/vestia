from __future__ import annotations
import itertools
from typing import List, Optional, Set
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.models import ClothingItem, Outfit
from app.database.repositories.clothing_repo import ClothingRepository
from app.database.repositories.outfit_repo import OutfitRepository
from app.database.repositories.history_repo import HistoryRepository
from app.rules.occasion_rules import (
    get_required_categories,
    get_optional_categories,
    CATEGORY_TO_POSITION,
    VALID_OCCASIONS,
)
from app.rules.scoring_engine import score_combination

# Cap candidates per category to keep the combinatorial search tractable.
# Items are sorted by wear_count ascending first, so the least-worn pieces
# (i.e. the ones most due for rotation) are preferred among the candidates.
MAX_CANDIDATES_PER_CATEGORY = 6


class OutfitService:

    def __init__(self, db: Session) -> None:
        self.clothing_repo = ClothingRepository(db)
        self.outfit_repo = OutfitRepository(db)
        self.history_repo = HistoryRepository(db)

    def _fetch_candidates(self, user_id: int, category: str, season: str) -> List[ClothingItem]:
        items = self.clothing_repo.get_by_category(user_id, category, season)
        items.sort(key=lambda i: i.wear_count)
        return items[:MAX_CANDIDATES_PER_CATEGORY]

    def generate_outfits(
        self,
        user_id: int,
        occasion: str,
        season: str,
        count: int = 3,
        extra_recently_worn_ids: Optional[Set[int]] = None,
    ) -> List[Outfit]:
        if occasion not in VALID_OCCASIONS:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown occasion '{occasion}'. Valid: {sorted(VALID_OCCASIONS)}",
            )

        recently_worn = self.history_repo.get_recently_worn_item_ids(user_id, days=2)
        if extra_recently_worn_ids:
            recently_worn = recently_worn | extra_recently_worn_ids

        required = get_required_categories(occasion)
        optional = get_optional_categories(occasion)

        # ── Gather candidates per category ────────────────────────────────────
        category_candidates: dict[str, list] = {}

        for cat in required:
            candidates = self._fetch_candidates(user_id, cat, season)
            if not candidates:
                raise HTTPException(
                    status_code=422,
                    detail=(
                        f"Wardrobe is missing '{cat}' items for occasion "
                        f"'{occasion}' (season: {season})."
                    ),
                )
            category_candidates[cat] = candidates

        for cat in optional:
            candidates = self._fetch_candidates(user_id, cat, season)
            # None = "skip this optional slot" — always a valid choice
            category_candidates[cat] = candidates + [None]

        # ── Build all combinations and score them ─────────────────────────────
        category_order = list(category_candidates.keys())
        value_lists = [category_candidates[cat] for cat in category_order]

        candidates_scored = []
        for combo in itertools.product(*value_lists):
            items = [item for item in combo if item is not None]
            scores = score_combination(items, occasion, season, recently_worn)
            candidates_scored.append((items, scores))

        candidates_scored.sort(key=lambda x: x[1]["total_score"], reverse=True)

        # ── Persist top-N outfits ───────────────────────────────────────────────
        results = []
        for items, scores in candidates_scored[:count]:
            outfit_data = {
                "occasion": occasion,
                "season": season,
                **scores,
            }
            outfit_items = [
                {
                    "clothing_item_id": item.id,
                    "position": CATEGORY_TO_POSITION[item.category],
                }
                for item in items
            ]
            outfit = self.outfit_repo.create(user_id, outfit_data, outfit_items)
            results.append(outfit)

        return results

    def get_outfit(self, outfit_id: int) -> Outfit:
        outfit = self.outfit_repo.get_by_id(outfit_id)
        if not outfit:
            raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found.")
        return outfit

    def list_outfits(
        self,
        user_id: int,
        occasion: Optional[str] = None,
        season: Optional[str] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Outfit]:
        return self.outfit_repo.get_all(user_id, occasion=occasion, season=season, skip=skip, limit=limit)

    def mark_worn(
        self,
        user_id: int,
        outfit_id: int,
        worn_date=None,
        occasion: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> None:
        outfit = self.get_outfit(outfit_id)
        if outfit.user_id != user_id:
            raise HTTPException(status_code=403, detail="Not your outfit.")

        self.history_repo.record_worn(user_id, outfit_id, worn_date, occasion, notes)

        for oi in outfit.items:
            self.clothing_repo.increment_wear_count(oi.clothing_item_id)

    def delete_outfit(self, outfit_id: int) -> None:
        removed = self.outfit_repo.delete(outfit_id)
        if not removed:
            raise HTTPException(status_code=404, detail=f"Outfit {outfit_id} not found.")
