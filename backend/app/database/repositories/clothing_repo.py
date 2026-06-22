from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.database.models import ClothingItem


class ClothingRepository:
    """All SQL for clothing_items lives here. Services call this — never raw ORM."""

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Create ────────────────────────────────────────────────────────────────

    def create(self, user_id: int, data: dict) -> ClothingItem:
        item = ClothingItem(user_id=user_id, **data)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        return item

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_by_id(self, item_id: int) -> Optional[ClothingItem]:
        return self.db.query(ClothingItem).filter(ClothingItem.id == item_id).first()

    def get_all(
        self,
        user_id: int,
        *,
        category: Optional[str] = None,
        style: Optional[str] = None,
        season: Optional[str] = None,
        color: Optional[str] = None,
        pattern: Optional[str] = None,
        is_active: bool = True,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ClothingItem]:
        q = self.db.query(ClothingItem).filter(
            ClothingItem.user_id == user_id,
            ClothingItem.is_active == is_active,
        )
        if category:
            q = q.filter(ClothingItem.category == category)
        if style:
            q = q.filter(ClothingItem.style == style)
        if season:
            q = q.filter(
                (ClothingItem.season == season) | (ClothingItem.season == "all_season")
            )
        if color:
            q = q.filter(
                (ClothingItem.primary_color.ilike(f"%{color}%")) |
                (ClothingItem.secondary_color.ilike(f"%{color}%"))
            )
        if pattern:
            q = q.filter(ClothingItem.pattern == pattern)

        return q.offset(skip).limit(limit).all()

    def get_by_category(self, user_id: int, category: str, season: Optional[str] = None) -> List[ClothingItem]:
        q = self.db.query(ClothingItem).filter(
            ClothingItem.user_id == user_id,
            ClothingItem.category == category,
            ClothingItem.is_active == True,
        )
        if season:
            q = q.filter(
                (ClothingItem.season == season) | (ClothingItem.season == "all_season")
            )
        return q.all()

    def count(self, user_id: int, *, is_active: bool = True) -> int:
        return (
            self.db.query(ClothingItem)
            .filter(ClothingItem.user_id == user_id, ClothingItem.is_active == is_active)
            .count()
        )

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, item_id: int, data: dict) -> Optional[ClothingItem]:
        item = self.get_by_id(item_id)
        if not item:
            return None
        for key, value in data.items():
            if value is not None:
                setattr(item, key, value)
        self.db.commit()
        self.db.refresh(item)
        return item

    def increment_wear_count(self, item_id: int) -> None:
        from datetime import datetime, timezone
        item = self.get_by_id(item_id)
        if item:
            item.wear_count += 1
            item.last_worn = datetime.now(timezone.utc)
            self.db.commit()

    def save_embedding(self, item_id: int, embedding_json: str) -> None:
        item = self.get_by_id(item_id)
        if item:
            item.embedding = embedding_json
            self.db.commit()

    # ── Delete ────────────────────────────────────────────────────────────────

    def soft_delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False
        item.is_active = False
        self.db.commit()
        return True

    def hard_delete(self, item_id: int) -> bool:
        item = self.get_by_id(item_id)
        if not item:
            return False
        self.db.delete(item)
        self.db.commit()
        return True
