from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session, joinedload

from app.database.models import Outfit, OutfitItem


class OutfitRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Create ────────────────────────────────────────────────────────────────

    def create(self, user_id: int, outfit_data: dict, items: list[dict]) -> Outfit:
        """
        outfit_data keys: name, occasion, season, total_score, color_score,
                          style_score, occasion_score, season_score, repetition_score
        items: [{"clothing_item_id": int, "position": str}, ...]
        """
        outfit = Outfit(user_id=user_id, **outfit_data)
        self.db.add(outfit)
        self.db.flush()                     # get outfit.id without full commit

        for item in items:
            oi = OutfitItem(outfit_id=outfit.id, **item)
            self.db.add(oi)

        self.db.commit()
        self.db.refresh(outfit)
        return outfit

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, outfit_id: int) -> Optional[Outfit]:
        return (
            self.db.query(Outfit)
            .options(
                joinedload(Outfit.items).joinedload(OutfitItem.clothing_item)
            )
            .filter(Outfit.id == outfit_id)
            .first()
        )

    def get_all(
        self,
        user_id: int,
        *,
        occasion: Optional[str] = None,
        season: Optional[str] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> List[Outfit]:
        q = (
            self.db.query(Outfit)
            .options(joinedload(Outfit.items).joinedload(OutfitItem.clothing_item))
            .filter(Outfit.user_id == user_id)
        )
        if occasion:
            q = q.filter(Outfit.occasion == occasion)
        if season:
            q = q.filter(Outfit.season == season)
        return q.order_by(Outfit.total_score.desc()).offset(skip).limit(limit).all()

    def get_top_scored(self, user_id: int, occasion: str, season: str, limit: int = 5) -> List[Outfit]:
        return (
            self.db.query(Outfit)
            .options(joinedload(Outfit.items).joinedload(OutfitItem.clothing_item))
            .filter(
                Outfit.user_id == user_id,
                Outfit.occasion == occasion,
                Outfit.season == season,
            )
            .order_by(Outfit.total_score.desc())
            .limit(limit)
            .all()
        )

    def count(self, user_id: int) -> int:
        return self.db.query(Outfit).filter(Outfit.user_id == user_id).count()

    # ── Items belonging to an outfit ─────────────────────────────────────────

    def get_item_ids(self, outfit_id: int) -> List[int]:
        rows = (
            self.db.query(OutfitItem.clothing_item_id)
            .filter(OutfitItem.outfit_id == outfit_id)
            .all()
        )
        return [r[0] for r in rows]

    # ── Delete ────────────────────────────────────────────────────────────────

    def delete(self, outfit_id: int) -> bool:
        outfit = self.db.query(Outfit).filter(Outfit.id == outfit_id).first()
        if not outfit:
            return False
        self.db.delete(outfit)
        self.db.commit()
        return True
