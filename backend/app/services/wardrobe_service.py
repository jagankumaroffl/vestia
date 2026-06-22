from __future__ import annotations
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.database.models import ClothingItem
from app.database.repositories.clothing_repo import ClothingRepository
from app.schemas.clothing import ClothingItemCreate, ClothingItemUpdate


class WardrobeService:

    def __init__(self, db: Session) -> None:
        self.repo = ClothingRepository(db)

    def add_item(
        self,
        user_id: int,
        image_path: str,
        cv_metadata: dict,
        user_overrides: Optional[ClothingItemCreate] = None,
    ) -> ClothingItem:
        """
        Merge CV-extracted metadata with optional user corrections,
        then persist to DB.
        """
        data = {
            "image_path": image_path,
            "category": cv_metadata.get("category"),
            "subcategory": cv_metadata.get("subcategory"),
            "primary_color": cv_metadata.get("primary_color"),
            "secondary_color": cv_metadata.get("secondary_color"),
            "pattern": cv_metadata.get("pattern", "solid"),
            "style": cv_metadata.get("style"),
            "season": cv_metadata.get("season", "all_season"),
            "gender": cv_metadata.get("gender", "unisex"),
            "embedding": cv_metadata.get("embedding"),
            "tags": [],
        }

        # User corrections override CV output
        if user_overrides:
            overrides = user_overrides.model_dump(exclude_none=True, exclude={"tags"})
            data.update(overrides)
            data["tags"] = user_overrides.tags

        return self.repo.create(user_id, data)

    def get_item(self, item_id: int) -> ClothingItem:
        item = self.repo.get_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found.")
        return item

    def list_items(
        self,
        user_id: int,
        *,
        category: Optional[str] = None,
        style: Optional[str] = None,
        season: Optional[str] = None,
        color: Optional[str] = None,
        pattern: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ClothingItem]:
        return self.repo.get_all(
            user_id,
            category=category,
            style=style,
            season=season,
            color=color,
            pattern=pattern,
            skip=skip,
            limit=limit,
        )

    def update_item(self, item_id: int, updates: ClothingItemUpdate) -> ClothingItem:
        updated = self.repo.update(item_id, updates.model_dump(exclude_none=True))
        if not updated:
            raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found.")
        return updated

    def delete_item(self, item_id: int) -> None:
        removed = self.repo.soft_delete(item_id)
        if not removed:
            raise HTTPException(status_code=404, detail=f"Clothing item {item_id} not found.")

    def count(self, user_id: int) -> int:
        return self.repo.count(user_id)
