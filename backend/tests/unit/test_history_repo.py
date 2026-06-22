"""Unit tests for HistoryRepository."""
from datetime import datetime, timedelta, timezone
import pytest
from app.database.repositories.history_repo import HistoryRepository
from app.database.repositories.outfit_repo import OutfitRepository


def _make_outfit(db, user_id=1):
    return OutfitRepository(db).create(
        user_id,
        dict(occasion="casual", season="all_season",
             total_score=0.7, color_score=0.7, style_score=0.7,
             occasion_score=0.7, season_score=1.0, repetition_score=1.0),
        [],
    )


class TestHistoryRecord:
    def test_record_worn_creates_entry(self, db, seed_user):
        outfit = _make_outfit(db)
        repo = HistoryRepository(db)
        entry = repo.record_worn(seed_user.id, outfit.id)
        assert entry.id is not None
        assert entry.outfit_id == outfit.id

    def test_record_worn_with_custom_date(self, db, seed_user):
        outfit = _make_outfit(db)
        dt = datetime(2024, 6, 15, tzinfo=timezone.utc)
        entry = HistoryRepository(db).record_worn(seed_user.id, outfit.id, worn_date=dt)
        # SQLite strips tzinfo on read; compare naive datetimes
        assert entry.worn_date.replace(tzinfo=None) == dt.replace(tzinfo=None)

    def test_record_worn_with_notes(self, db, seed_user):
        outfit = _make_outfit(db)
        entry = HistoryRepository(db).record_worn(
            seed_user.id, outfit.id, notes="Great day!", occasion="office"
        )
        assert entry.notes == "Great day!"
        assert entry.occasion == "office"


class TestHistoryQuery:
    def test_get_recent_within_days(self, db, seed_user):
        outfit = _make_outfit(db)
        repo = HistoryRepository(db)

        # One entry 1 day ago (within range)
        repo.record_worn(
            seed_user.id, outfit.id,
            worn_date=datetime.now(timezone.utc) - timedelta(days=1)
        )
        # One entry 10 days ago (outside range)
        repo.record_worn(
            seed_user.id, outfit.id,
            worn_date=datetime.now(timezone.utc) - timedelta(days=10)
        )

        recent = repo.get_recent(seed_user.id, days=7)
        assert len(recent) == 1

    def test_get_recently_worn_item_ids_empty_when_no_history(self, db, seed_user, seed_clothing):
        ids = HistoryRepository(db).get_recently_worn_item_ids(seed_user.id, days=2)
        assert ids == set()

    def test_get_recently_worn_item_ids_includes_outfit_items(self, db, seed_user, seed_clothing):
        top    = seed_clothing["t-shirt"]
        bottom = seed_clothing["jeans"]
        outfit = OutfitRepository(db).create(
            seed_user.id,
            dict(occasion="casual", season="all_season",
                 total_score=0.7, color_score=0.7, style_score=0.7,
                 occasion_score=0.7, season_score=1.0, repetition_score=1.0),
            [
                {"clothing_item_id": top.id,    "position": "top"},
                {"clothing_item_id": bottom.id, "position": "bottom"},
            ],
        )
        repo = HistoryRepository(db)
        repo.record_worn(
            seed_user.id, outfit.id,
            worn_date=datetime.now(timezone.utc) - timedelta(hours=6)
        )
        worn_ids = repo.get_recently_worn_item_ids(seed_user.id, days=1)
        assert top.id in worn_ids
        assert bottom.id in worn_ids

    def test_count_worn(self, db, seed_user):
        outfit = _make_outfit(db)
        repo = HistoryRepository(db)
        repo.record_worn(seed_user.id, outfit.id)
        repo.record_worn(seed_user.id, outfit.id)
        assert repo.count_worn(seed_user.id) == 2

    def test_get_all_pagination(self, db, seed_user):
        outfit = _make_outfit(db)
        repo = HistoryRepository(db)
        for _ in range(5):
            repo.record_worn(seed_user.id, outfit.id)

        page1 = repo.get_all(seed_user.id, skip=0, limit=3)
        page2 = repo.get_all(seed_user.id, skip=3, limit=3)
        assert len(page1) == 3
        assert len(page2) == 2
