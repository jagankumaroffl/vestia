"""Unit tests for the combined scoring engine."""
from app.rules.scoring_engine import (
    score_combination,
    WEIGHT_COLOR, WEIGHT_STYLE, WEIGHT_OCCASION, WEIGHT_SEASON, WEIGHT_REPETITION,
)


class FakeItem:
    def __init__(self, item_id, category, style, season, primary_color, secondary_color=None):
        self.id = item_id
        self.category = category
        self.style = style
        self.season = season
        self.primary_color = primary_color
        self.secondary_color = secondary_color


def _good_casual_outfit():
    return [
        FakeItem(1, "topwear",    "casual", "all_season", "white"),
        FakeItem(2, "bottomwear", "casual", "all_season", "navy blue"),
        FakeItem(3, "footwear",   "casual", "all_season", "white"),
    ]


class TestWeights:
    def test_weights_sum_to_one(self):
        total = WEIGHT_COLOR + WEIGHT_STYLE + WEIGHT_OCCASION + WEIGHT_SEASON + WEIGHT_REPETITION
        assert abs(total - 1.0) < 1e-9

    def test_color_weight_is_largest(self):
        assert WEIGHT_COLOR == max(WEIGHT_COLOR, WEIGHT_STYLE, WEIGHT_OCCASION, WEIGHT_SEASON, WEIGHT_REPETITION)

    def test_repetition_weight_is_smallest(self):
        assert WEIGHT_REPETITION == min(WEIGHT_COLOR, WEIGHT_STYLE, WEIGHT_OCCASION, WEIGHT_SEASON, WEIGHT_REPETITION)


class TestScoreCombination:
    def test_returns_all_required_keys(self):
        items = _good_casual_outfit()
        result = score_combination(items, "casual", "all_season", set())
        expected_keys = {
            "total_score", "color_score", "style_score",
            "occasion_score", "season_score", "repetition_score",
        }
        assert set(result.keys()) == expected_keys

    def test_all_scores_in_range(self):
        items = _good_casual_outfit()
        result = score_combination(items, "casual", "all_season", set())
        for key, value in result.items():
            assert 0.0 <= value <= 1.0, f"{key}={value} out of range"

    def test_perfect_outfit_scores_high(self):
        """All-neutral, all-casual, all-season, no repeats → near-perfect score."""
        items = _good_casual_outfit()
        result = score_combination(items, "casual", "all_season", set())
        assert result["total_score"] > 0.9

    def test_total_score_matches_weighted_sum(self):
        items = _good_casual_outfit()
        result = score_combination(items, "casual", "all_season", set())
        expected_total = round(
            result["color_score"]      * WEIGHT_COLOR +
            result["style_score"]      * WEIGHT_STYLE +
            result["occasion_score"]   * WEIGHT_OCCASION +
            result["season_score"]     * WEIGHT_SEASON +
            result["repetition_score"] * WEIGHT_REPETITION,
            4,
        )
        assert result["total_score"] == expected_total

    def test_repetition_lowers_total_score(self):
        items = _good_casual_outfit()
        no_repeat = score_combination(items, "casual", "all_season", set())
        with_repeat = score_combination(items, "casual", "all_season", {1, 2})
        assert with_repeat["total_score"] < no_repeat["total_score"]
        assert with_repeat["repetition_score"] < no_repeat["repetition_score"]

    def test_wrong_season_lowers_score(self):
        winter_items = [
            FakeItem(1, "topwear",    "casual", "winter", "white"),
            FakeItem(2, "bottomwear", "casual", "winter", "navy blue"),
            FakeItem(3, "footwear",   "casual", "winter", "white"),
        ]
        summer_score = score_combination(winter_items, "casual", "summer", set())
        winter_score = score_combination(winter_items, "casual", "winter", set())
        assert summer_score["season_score"] < winter_score["season_score"]
        assert summer_score["total_score"] < winter_score["total_score"]

    def test_clashing_colors_lower_score(self):
        clash_items = [
            FakeItem(1, "topwear",    "casual", "all_season", "red"),
            FakeItem(2, "bottomwear", "casual", "all_season", "light purple"),
            FakeItem(3, "footwear",   "casual", "all_season", "white"),
        ]
        good_items = _good_casual_outfit()

        clash_score = score_combination(clash_items, "casual", "all_season", set())
        good_score = score_combination(good_items, "casual", "all_season", set())

        assert clash_score["color_score"] < good_score["color_score"]
        assert clash_score["total_score"] < good_score["total_score"]

    def test_wrong_style_for_occasion_lowers_score(self):
        sporty_items = [
            FakeItem(1, "topwear",    "sports", "all_season", "white"),
            FakeItem(2, "bottomwear", "sports", "all_season", "navy blue"),
            FakeItem(3, "footwear",   "sports", "all_season", "white"),
            FakeItem(4, "outerwear",  "sports", "all_season", "black"),
        ]
        formal_items = [
            FakeItem(5, "topwear",    "formal", "all_season", "white"),
            FakeItem(6, "bottomwear", "formal", "all_season", "black"),
            FakeItem(7, "footwear",   "formal", "all_season", "black"),
            FakeItem(8, "outerwear",  "formal", "all_season", "black"),
        ]
        sporty_score = score_combination(sporty_items, "formal_event", "all_season", set())
        formal_score = score_combination(formal_items, "formal_event", "all_season", set())

        assert sporty_score["occasion_score"] < formal_score["occasion_score"]
        assert sporty_score["total_score"] < formal_score["total_score"]
