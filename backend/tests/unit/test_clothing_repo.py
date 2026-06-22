"""Unit tests for ClothingRepository."""
import pytest
from app.database.repositories.clothing_repo import ClothingRepository


def _make_item(db, user_id=1, **overrides):
    defaults = dict(
        category="topwear", subcategory="t-shirt",
        primary_color="white", pattern="solid",
        style="casual", season="all_season",
        gender="unisex", image_path="1/test.jpg",
    )
    defaults.update(overrides)
    return ClothingRepository(db).create(user_id, defaults)


class TestClothingCreate:
    def test_create_returns_item_with_id(self, db, seed_user):
        item = _make_item(db)
        assert item.id is not None
        assert item.category == "topwear"

    def test_default_wear_count_is_zero(self, db, seed_user):
        item = _make_item(db)
        assert item.wear_count == 0
        assert item.is_active is True

    def test_create_with_all_fields(self, db, seed_user):
        item = _make_item(db, subcategory="polo", primary_color="navy blue",
                          secondary_color="white", style="smart_casual")
        assert item.subcategory == "polo"
        assert item.secondary_color == "white"


class TestClothingRead:
    def test_get_by_id(self, db, seed_user):
        item = _make_item(db)
        repo = ClothingRepository(db)
        found = repo.get_by_id(item.id)
        assert found is not None
        assert found.id == item.id

    def test_get_by_id_missing_returns_none(self, db, seed_user):
        assert ClothingRepository(db).get_by_id(9999) is None

    def test_get_all_returns_active_only(self, db, seed_user):
        repo = ClothingRepository(db)
        item = _make_item(db)
        repo.soft_delete(item.id)
        active = repo.get_all(seed_user.id)
        assert all(i.id != item.id for i in active)

    def test_get_all_filter_by_category(self, db, seed_user, seed_clothing):
        repo = ClothingRepository(db)
        tops = repo.get_all(seed_user.id, category="topwear")
        assert all(i.category == "topwear" for i in tops)
        assert len(tops) >= 1

    def test_get_all_filter_by_season(self, db, seed_user):
        repo = ClothingRepository(db)
        _make_item(db, season="summer")
        _make_item(db, season="winter")
        summer = repo.get_all(seed_user.id, season="summer")
        # all_season items also returned
        assert all(i.season in ("summer", "all_season") for i in summer)

    def test_get_by_category(self, db, seed_user, seed_clothing):
        repo = ClothingRepository(db)
        bottoms = repo.get_by_category(seed_user.id, "bottomwear")
        assert len(bottoms) >= 1
        assert all(i.category == "bottomwear" for i in bottoms)

    def test_count(self, db, seed_user, seed_clothing):
        count = ClothingRepository(db).count(seed_user.id)
        assert count >= 3


class TestClothingUpdate:
    def test_update_color(self, db, seed_user):
        item = _make_item(db)
        repo = ClothingRepository(db)
        updated = repo.update(item.id, {"primary_color": "black"})
        assert updated.primary_color == "black"

    def test_update_nonexistent_returns_none(self, db, seed_user):
        assert ClothingRepository(db).update(9999, {"style": "formal"}) is None

    def test_increment_wear_count(self, db, seed_user):
        item = _make_item(db)
        repo = ClothingRepository(db)
        repo.increment_wear_count(item.id)
        repo.increment_wear_count(item.id)
        refreshed = repo.get_by_id(item.id)
        assert refreshed.wear_count == 2
        assert refreshed.last_worn is not None


class TestClothingDelete:
    def test_soft_delete_sets_inactive(self, db, seed_user):
        item = _make_item(db)
        repo = ClothingRepository(db)
        assert repo.soft_delete(item.id) is True
        assert repo.get_by_id(item.id).is_active is False

    def test_soft_delete_nonexistent_returns_false(self, db, seed_user):
        assert ClothingRepository(db).soft_delete(9999) is False

    def test_hard_delete_removes_row(self, db, seed_user):
        item = _make_item(db)
        repo = ClothingRepository(db)
        assert repo.hard_delete(item.id) is True
        assert repo.get_by_id(item.id) is None
