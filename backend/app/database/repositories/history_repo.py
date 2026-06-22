from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Set
from sqlalchemy.orm import Session

from app.database.models import OutfitHistory, OutfitItem


class HistoryRepository:

    def __init__(self, db: Session) -> None:
        self.db = db

    # ── Write ─────────────────────────────────────────────────────────────────

    def record_worn(
        self,
        user_id: int,
        outfit_id: int,
        worn_date: Optional[datetime] = None,
        occasion: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> OutfitHistory:
        entry = OutfitHistory(
            user_id=user_id,
            outfit_id=outfit_id,
            worn_date=worn_date or datetime.now(timezone.utc),
            occasion=occasion,
            notes=notes,
        )
        self.db.add(entry)
        self.db.commit()
        self.db.refresh(entry)
        return entry

    # ── Read ──────────────────────────────────────────────────────────────────

    def get_recent(self, user_id: int, days: int = 7) -> List[OutfitHistory]:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        return (
            self.db.query(OutfitHistory)
            .filter(
                OutfitHistory.user_id == user_id,
                OutfitHistory.worn_date >= cutoff,
            )
            .order_by(OutfitHistory.worn_date.desc())
            .all()
        )

    def get_recently_worn_item_ids(self, user_id: int, days: int = 2) -> Set[int]:
        """
        Returns clothing item ids worn within the last `days` days.
        Used by the repetition penalty in the scoring engine.
        """
        recent_history = self.get_recent(user_id, days=days)
        outfit_ids = {h.outfit_id for h in recent_history}
        if not outfit_ids:
            return set()

        rows = (
            self.db.query(OutfitItem.clothing_item_id)
            .filter(OutfitItem.outfit_id.in_(outfit_ids))
            .all()
        )
        return {r[0] for r in rows}

    def count_worn(self, user_id: int) -> int:
        return (
            self.db.query(OutfitHistory)
            .filter(OutfitHistory.user_id == user_id)
            .count()
        )

    def get_all(self, user_id: int, skip: int = 0, limit: int = 50) -> List[OutfitHistory]:
        return (
            self.db.query(OutfitHistory)
            .filter(OutfitHistory.user_id == user_id)
            .order_by(OutfitHistory.worn_date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
