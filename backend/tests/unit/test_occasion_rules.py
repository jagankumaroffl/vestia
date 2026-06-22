"""Unit tests for occasion rules."""
import pytest
from app.rules.occasion_rules import (
    OCCASION_RULES,
    VALID_OCCASIONS,
    get_required_categories,
    get_optional_categories,
    score_style_for_occasion,
    score_occasion_match,
    CATEGORY_TO_POSITION,
)


class FakeItem:
    def __init__(self, category, style):
        self.category = category
        self.style = style


class TestOccasionDefinitions:
    def test_nine_occasions_defined(self):
        assert len(VALID_OCCASIONS) == 9

    def test_expected_occasions_present(self):
        expected = {
            "casual", "college", "office", "business_meeting",
            "formal_event", "party", "date_night", "wedding", "travel",
        }
        assert expected == VALID_OCCASIONS

    def test_all_occasions_require_base_categories(self):
        for occasion, rules in OCCASION_RULES.items():
            required = set(rules["required_categories"])
            assert {"topwear", "bottomwear", "footwear"}.issubset(required)

    def test_formal_event_requires_outerwear(self):
        assert "outerwear" in get_required_categories("formal_event")

    def test_wedding_requires_outerwear(self):
        assert "outerwear" in get_required_categories("wedding")

    def test_casual_does_not_require_outerwear(self):
        assert "outerwear" not in get_required_categories("casual")

    def test_unknown_occasion_returns_default(self):
        assert get_required_categories("unknown") == ["topwear", "bottomwear", "footwear"]
        assert get_optional_categories("unknown") == []


class TestCategoryToPosition:
    def test_all_categories_mapped(self):
        for cat in ["topwear", "bottomwear", "footwear", "outerwear", "accessory"]:
            assert cat in CATEGORY_TO_POSITION


class TestScoreStyleForOccasion:
    def test_top_ranked_style_scores_one(self):
        assert score_style_for_occasion("formal", "formal_event") == 1.0

    def test_second_ranked_style_decays(self):
        # office: ["business_casual", "smart_casual", "formal"]
        assert score_style_for_occasion("smart_casual", "office") == 0.8

    def test_third_ranked_style(self):
        assert score_style_for_occasion("formal", "office") == 0.6

    def test_unlisted_style_scores_low(self):
        assert score_style_for_occasion("sports", "formal_event") == 0.20

    def test_unknown_occasion_returns_neutral(self):
        assert score_style_for_occasion("casual", "unknown_occasion") == 0.5


class TestScoreOccasionMatch:
    def test_complete_outfit_with_preferred_style(self):
        items = [
            FakeItem("topwear", "casual"),
            FakeItem("bottomwear", "casual"),
            FakeItem("footwear", "casual"),
        ]
        score = score_occasion_match(items, "casual")
        # All categories present (structural=1.0) + style perfectly matches (1.0)
        assert score == 1.0

    def test_missing_required_category_penalized(self):
        # formal_event requires outerwear too — missing it
        items = [
            FakeItem("topwear", "formal"),
            FakeItem("bottomwear", "formal"),
            FakeItem("footwear", "formal"),
        ]
        score = score_occasion_match(items, "formal_event")
        complete_items = items + [FakeItem("outerwear", "formal")]
        complete_score = score_occasion_match(complete_items, "formal_event")
        assert score < complete_score

    def test_empty_items_returns_zero(self):
        assert score_occasion_match([], "casual") == 0.0

    def test_unknown_occasion_returns_neutral(self):
        items = [FakeItem("topwear", "casual")]
        assert score_occasion_match(items, "unknown") == 0.5

    def test_wrong_style_for_occasion_scores_lower(self):
        # casual items for a formal_event
        casual_items = [
            FakeItem("topwear", "casual"),
            FakeItem("bottomwear", "casual"),
            FakeItem("footwear", "casual"),
            FakeItem("outerwear", "casual"),
        ]
        formal_items = [
            FakeItem("topwear", "formal"),
            FakeItem("bottomwear", "formal"),
            FakeItem("footwear", "formal"),
            FakeItem("outerwear", "formal"),
        ]
        casual_score = score_occasion_match(casual_items, "formal_event")
        formal_score = score_occasion_match(formal_items, "formal_event")
        assert formal_score > casual_score
