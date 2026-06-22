"""
Integration tests — full round-trip across repositories + services.

Uses the same in-memory SQLite fixture as unit tests.
"""
import pytest
from app.database.repositories.user_repo import UserRepository
from app.database.repositories.clothing_repo import ClothingRepository
from app.database.repositories.outfit_repo import OutfitRepository
from app.database.repositories.history_repo import HistoryRepository
from app.database.repositories.stats_repo import StatsRepository


class TestUserFlow:
    def test_create_user_and_preferences(self, db):
        repo = UserRepository(db)
        user = repo.create("jagan", "jagan@test.com", body_type="athletic")
        assert user.id is not None

        prefs = repo.get_preferences(user.id)
        assert prefs is not None
        assert prefs.user_id == user.id

    def test_update_preferences(self, db):
        repo = UserRepository(db)
        user = repo.create("jagan2", "jagan2@test.com")
        repo.update_preferences(user.id, {"preferred_styles": ["casual","formal"]})
        prefs = repo.get_preferences(user.id)
        assert prefs.preferred_styles == ["casual","formal"]

    def test_get_or_create_default(self, db):
        repo = UserRepository(db)
        u1 = repo.get_or_create_default()
        u2 = repo.get_or_create_default()
        assert u1.id == u2.id     # idempotent


class TestWardrobeFlow:
    def test_add_and_retrieve_item(self, db, seed_user):
        repo = ClothingRepository(db)
        item = repo.create(seed_user.id, {
            "image_path": "1/shirt.jpg",
            "category": "topwear", "subcategory": "t-shirt",
            "primary_color": "white", "pattern": "solid",
            "style": "casual", "season": "summer",
            "gender": "unisex",
        })
        found = repo.get_by_id(item.id)
        assert found.primary_color == "white"

    def test_filter_by_multiple_criteria(self, db, seed_user, seed_clothing):
        repo = ClothingRepository(db)
        # formal topwear
        results = repo.get_all(seed_user.id, category="topwear", style="formal")
        assert all(i.category == "topwear" and i.style == "formal" for i in results)


class TestOutfitHistoryFlow:
    def test_generate_outfit_and_mark_worn(self, db, seed_user, seed_clothing):
        top    = seed_clothing["t-shirt"]
        bottom = seed_clothing["jeans"]
        shoes  = seed_clothing["sneakers"]

        # Create outfit
        outfit = OutfitRepository(db).create(
            seed_user.id,
            dict(occasion="casual", season="all_season",
                 total_score=0.8, color_score=0.8, style_score=0.8,
                 occasion_score=0.8, season_score=1.0, repetition_score=1.0),
            [
                {"clothing_item_id": top.id,    "position": "top"},
                {"clothing_item_id": bottom.id, "position": "bottom"},
                {"clothing_item_id": shoes.id,  "position": "shoes"},
            ],
        )

        # Mark worn
        hist_repo = HistoryRepository(db)
        hist_repo.record_worn(seed_user.id, outfit.id, occasion="casual")

        # Increment wear counts
        cloth_repo = ClothingRepository(db)
        for oi in outfit.items:
            cloth_repo.increment_wear_count(oi.clothing_item_id)

        # Verify wear counts
        assert cloth_repo.get_by_id(top.id).wear_count    == 1
        assert cloth_repo.get_by_id(bottom.id).wear_count == 1
        assert cloth_repo.get_by_id(shoes.id).wear_count  == 1
        assert hist_repo.count_worn(seed_user.id) == 1

    def test_repetition_detection(self, db, seed_user, seed_clothing):
        """Items worn yesterday must appear in recently_worn_item_ids."""
        from datetime import datetime, timedelta, timezone
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
        HistoryRepository(db).record_worn(
            seed_user.id, outfit.id,
            worn_date=datetime.now(timezone.utc) - timedelta(hours=20),
        )
        worn_ids = HistoryRepository(db).get_recently_worn_item_ids(seed_user.id, days=2)
        assert top.id    in worn_ids
        assert bottom.id in worn_ids


class TestStatsFlow:
    def test_compute_and_upsert(self, db, seed_user, seed_clothing):
        stats = StatsRepository(db).compute_and_upsert(seed_user.id)
        assert stats.total_items >= 3
        assert "topwear" in stats.category_breakdown
        assert "bottomwear" in stats.category_breakdown

    def test_stats_idempotent(self, db, seed_user, seed_clothing):
        repo = StatsRepository(db)
        s1 = repo.compute_and_upsert(seed_user.id)
        s2 = repo.compute_and_upsert(seed_user.id)
        assert s1.id == s2.id       # same row upserted

    def test_count_by_category(self, db, seed_user, seed_clothing):
        breakdown = StatsRepository(db).count_by_category(seed_user.id)
        assert breakdown.get("topwear", 0) >= 1

    def test_count_by_style(self, db, seed_user, seed_clothing):
        breakdown = StatsRepository(db).count_by_style(seed_user.id)
        assert len(breakdown) >= 1
