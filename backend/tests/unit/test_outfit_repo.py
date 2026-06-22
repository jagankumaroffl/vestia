"""Unit tests for OutfitRepository."""
import pytest
from app.database.repositories.outfit_repo import OutfitRepository


def _make_outfit(db, user_id=1, items=None):
    outfit_data = dict(
        occasion="casual", season="all_season",
        total_score=0.75, color_score=0.8,
        style_score=0.7, occasion_score=0.8,
        season_score=1.0, repetition_score=1.0,
    )
    item_payloads = items or []
    return OutfitRepository(db).create(user_id, outfit_data, item_payloads)


class TestOutfitCreate:
    def test_create_with_items(self, db, seed_user, seed_clothing):
        top    = seed_clothing["t-shirt"]
        bottom = seed_clothing["jeans"]
        shoes  = seed_clothing["sneakers"]

        outfit = _make_outfit(db, items=[
            {"clothing_item_id": top.id,    "position": "top"},
            {"clothing_item_id": bottom.id, "position": "bottom"},
            {"clothing_item_id": shoes.id,  "position": "shoes"},
        ])
        assert outfit.id is not None
        assert len(outfit.items) == 3

    def test_create_empty_outfit(self, db, seed_user):
        outfit = _make_outfit(db)
        assert outfit.id is not None
        assert outfit.items == []

    def test_scores_persisted(self, db, seed_user, seed_clothing):
        outfit = _make_outfit(db, items=[
            {"clothing_item_id": seed_clothing["t-shirt"].id, "position": "top"},
        ])
        assert outfit.total_score == 0.75
        assert outfit.color_score == 0.8


class TestOutfitRead:
    def test_get_by_id(self, db, seed_user, seed_clothing):
        outfit = _make_outfit(db, items=[
            {"clothing_item_id": seed_clothing["t-shirt"].id, "position": "top"},
        ])
        repo = OutfitRepository(db)
        found = repo.get_by_id(outfit.id)
        assert found is not None
        assert len(found.items) == 1
        assert found.items[0].clothing_item is not None  # joinedload works

    def test_get_by_id_missing_returns_none(self, db, seed_user):
        assert OutfitRepository(db).get_by_id(9999) is None

    def test_get_all_filters_occasion(self, db, seed_user, seed_clothing):
        repo = OutfitRepository(db)
        _make_outfit(db)   # casual
        # Create office outfit
        repo.create(seed_user.id,
                    dict(occasion="office", season="all_season",
                         total_score=0.8, color_score=0.8, style_score=0.8,
                         occasion_score=0.9, season_score=1.0, repetition_score=1.0),
                    [])
        casual = repo.get_all(seed_user.id, occasion="casual")
        assert all(o.occasion == "casual" for o in casual)

    def test_get_all_sorted_by_score(self, db, seed_user, seed_clothing):
        repo = OutfitRepository(db)
        for score in [0.5, 0.9, 0.7]:
            repo.create(seed_user.id,
                        dict(occasion="casual", season="all_season",
                             total_score=score, color_score=score, style_score=score,
                             occasion_score=score, season_score=1.0, repetition_score=1.0),
                        [])
        results = repo.get_all(seed_user.id)
        scores = [o.total_score for o in results]
        assert scores == sorted(scores, reverse=True)

    def test_get_item_ids(self, db, seed_user, seed_clothing):
        top    = seed_clothing["t-shirt"]
        bottom = seed_clothing["jeans"]
        outfit = _make_outfit(db, items=[
            {"clothing_item_id": top.id,    "position": "top"},
            {"clothing_item_id": bottom.id, "position": "bottom"},
        ])
        ids = OutfitRepository(db).get_item_ids(outfit.id)
        assert set(ids) == {top.id, bottom.id}

    def test_count(self, db, seed_user):
        repo = OutfitRepository(db)
        _make_outfit(db)
        _make_outfit(db)
        assert repo.count(seed_user.id) == 2


class TestOutfitDelete:
    def test_delete_removes_outfit_and_items(self, db, seed_user, seed_clothing):
        outfit = _make_outfit(db, items=[
            {"clothing_item_id": seed_clothing["t-shirt"].id, "position": "top"},
        ])
        repo = OutfitRepository(db)
        assert repo.delete(outfit.id) is True
        assert repo.get_by_id(outfit.id) is None

    def test_delete_nonexistent_returns_false(self, db, seed_user):
        assert OutfitRepository(db).delete(9999) is False
