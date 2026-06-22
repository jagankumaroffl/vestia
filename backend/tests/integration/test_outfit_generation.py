"""Integration tests — OutfitService.generate_outfits with the full rules engine."""
import pytest
from fastapi import HTTPException

from app.services.outfit_service import OutfitService
from app.database.models import ClothingItem


def _add_item(db, user_id, **kwargs):
    defaults = dict(
        image_path="1/item.jpg", secondary_color=None,
        pattern="solid", season="all_season", gender="unisex",
        wear_count=0,
    )
    defaults.update(kwargs)
    item = ClothingItem(user_id=user_id, **defaults)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


class TestGenerateOutfitsCasual:
    def test_generates_requested_count(self, db, seed_user, seed_clothing):
        service = OutfitService(db)
        outfits = service.generate_outfits(seed_user.id, "casual", "all_season", count=2)
        assert len(outfits) <= 2
        assert len(outfits) >= 1

    def test_outfit_has_required_positions(self, db, seed_user, seed_clothing):
        service = OutfitService(db)
        outfits = service.generate_outfits(seed_user.id, "casual", "all_season", count=1)
        positions = {oi.position for oi in outfits[0].items}
        assert {"top", "bottom", "shoes"}.issubset(positions)

    def test_scores_are_populated(self, db, seed_user, seed_clothing):
        service = OutfitService(db)
        outfits = service.generate_outfits(seed_user.id, "casual", "all_season", count=1)
        outfit = outfits[0]
        assert 0.0 <= outfit.total_score <= 1.0
        assert 0.0 <= outfit.color_score <= 1.0
        assert 0.0 <= outfit.style_score <= 1.0

    def test_results_sorted_by_score_descending(self, db, seed_user, seed_clothing):
        service = OutfitService(db)
        outfits = service.generate_outfits(seed_user.id, "casual", "all_season", count=3)
        scores = [o.total_score for o in outfits]
        assert scores == sorted(scores, reverse=True)


class TestGenerateOutfitsMissingWardrobe:
    def test_missing_topwear_raises_422(self, db, seed_user):
        # Only bottomwear + footwear, no topwear
        _add_item(db, seed_user.id, category="bottomwear", subcategory="jeans",
                  primary_color="navy blue", style="casual")
        _add_item(db, seed_user.id, category="footwear", subcategory="sneakers",
                  primary_color="white", style="casual")

        service = OutfitService(db)
        with pytest.raises(HTTPException) as exc_info:
            service.generate_outfits(seed_user.id, "casual", "all_season")
        assert exc_info.value.status_code == 422
        assert "topwear" in exc_info.value.detail

    def test_empty_wardrobe_raises_422(self, db, seed_user):
        service = OutfitService(db)
        with pytest.raises(HTTPException) as exc_info:
            service.generate_outfits(seed_user.id, "casual", "all_season")
        assert exc_info.value.status_code == 422


class TestGenerateOutfitsFormalEvent:
    def test_requires_outerwear(self, db, seed_user):
        # Topwear, bottomwear, footwear but NO outerwear
        _add_item(db, seed_user.id, category="topwear", subcategory="oxford shirt",
                  primary_color="white", style="formal")
        _add_item(db, seed_user.id, category="bottomwear", subcategory="formal trousers",
                  primary_color="black", style="formal")
        _add_item(db, seed_user.id, category="footwear", subcategory="formal shoes",
                  primary_color="black", style="formal")

        service = OutfitService(db)
        with pytest.raises(HTTPException) as exc_info:
            service.generate_outfits(seed_user.id, "formal_event", "all_season")
        assert exc_info.value.status_code == 422
        assert "outerwear" in exc_info.value.detail

    def test_succeeds_with_outerwear(self, db, seed_user):
        _add_item(db, seed_user.id, category="topwear", subcategory="oxford shirt",
                  primary_color="white", style="formal")
        _add_item(db, seed_user.id, category="bottomwear", subcategory="formal trousers",
                  primary_color="black", style="formal")
        _add_item(db, seed_user.id, category="footwear", subcategory="formal shoes",
                  primary_color="black", style="formal")
        _add_item(db, seed_user.id, category="outerwear", subcategory="blazer",
                  primary_color="black", style="formal")

        service = OutfitService(db)
        outfits = service.generate_outfits(seed_user.id, "formal_event", "all_season", count=1)
        assert len(outfits) == 1
        positions = {oi.position for oi in outfits[0].items}
        assert "outerwear" in positions


class TestGenerateOutfitsRepetition:
    def test_repetition_avoided_across_consecutive_days(self, db, seed_user, seed_clothing):
        """
        Generate an outfit, mark it worn, then generate again —
        the top/bottom from the worn outfit should be deprioritized.
        """
        service = OutfitService(db)

        # Day 1
        day1_outfits = service.generate_outfits(seed_user.id, "casual", "all_season", count=1)
        day1 = day1_outfits[0]
        service.mark_worn(seed_user.id, day1.id)

        day1_top_id = next(oi.clothing_item_id for oi in day1.items if oi.position == "top")
        day1_bottom_id = next(oi.clothing_item_id for oi in day1.items if oi.position == "bottom")

        # Day 2 — best-scored outfit should avoid yesterday's top+bottom combo
        # (only matters if alternatives exist; with limited seed data we just
        #  check repetition_score reflects the penalty when same items chosen)
        day2_outfits = service.generate_outfits(seed_user.id, "casual", "all_season", count=5)

        # At least one of the top results should have repetition_score < 1.0
        # if the same top or bottom appears, OR a fully fresh combo with score 1.0
        for outfit in day2_outfits:
            top_id = next((oi.clothing_item_id for oi in outfit.items if oi.position == "top"), None)
            bottom_id = next((oi.clothing_item_id for oi in outfit.items if oi.position == "bottom"), None)
            if top_id == day1_top_id or bottom_id == day1_bottom_id:
                assert outfit.repetition_score < 1.0
            else:
                assert outfit.repetition_score == 1.0


class TestGenerateOutfitsInvalidOccasion:
    def test_unknown_occasion_raises_422(self, db, seed_user, seed_clothing):
        service = OutfitService(db)
        with pytest.raises(HTTPException) as exc_info:
            service.generate_outfits(seed_user.id, "birthday_bash", "all_season")
        assert exc_info.value.status_code == 422
        assert "Unknown occasion" in exc_info.value.detail
