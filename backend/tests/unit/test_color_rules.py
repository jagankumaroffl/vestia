"""Unit tests for color matching rules."""
from app.rules.color_rules import (
    score_color_pair,
    score_color_combination,
    SCORE_IDENTICAL,
    SCORE_NEUTRAL,
    SCORE_COMPLEMENTARY,
    SCORE_ANALOGOUS,
)


class FakeItem:
    """Lightweight stand-in for ClothingItem ORM object."""
    def __init__(self, primary_color, secondary_color=None):
        self.primary_color = primary_color
        self.secondary_color = secondary_color


class TestScoreColorPair:
    def test_identical_colors(self):
        assert score_color_pair("navy blue", "navy blue") == SCORE_IDENTICAL

    def test_identical_after_alias_normalization(self):
        # "navy" normalizes to "navy blue"
        assert score_color_pair("navy", "navy blue") == SCORE_IDENTICAL

    def test_neutral_matches_anything(self):
        assert score_color_pair("black", "red") == SCORE_NEUTRAL
        assert score_color_pair("white", "burgundy") == SCORE_NEUTRAL
        assert score_color_pair("beige", "purple") == SCORE_NEUTRAL

    def test_both_neutral(self):
        assert score_color_pair("black", "white") == SCORE_NEUTRAL

    def test_complementary_blue_orange(self):
        assert score_color_pair("blue", "orange") == SCORE_COMPLEMENTARY

    def test_complementary_purple_yellow(self):
        assert score_color_pair("purple", "yellow") == SCORE_COMPLEMENTARY

    def test_complementary_red_green(self):
        assert score_color_pair("red", "green") == SCORE_COMPLEMENTARY

    def test_complementary_symmetric(self):
        # Order shouldn't matter
        assert score_color_pair("orange", "blue") == score_color_pair("blue", "orange")

    def test_analogous_blue_lightgreen(self):
        assert score_color_pair("blue", "light green") == SCORE_ANALOGOUS

    def test_analogous_blue_purple(self):
        assert score_color_pair("blue", "purple") == SCORE_ANALOGOUS

    def test_clashing_colors_score_low(self):
        # Mid-distance hues that aren't analogous/complementary should
        # score below the analogous threshold
        score = score_color_pair("red", "light purple")
        assert 0.0 <= score < SCORE_ANALOGOUS

    def test_score_always_in_range(self):
        colors = ["red", "blue", "green", "yellow", "purple", "orange",
                  "black", "white", "grey", "beige", "pink", "burgundy"]
        for c1 in colors:
            for c2 in colors:
                score = score_color_pair(c1, c2)
                assert 0.0 <= score <= 1.0, f"{c1}/{c2} → {score} out of range"


class TestScoreColorCombination:
    def test_single_item_returns_one(self):
        items = [FakeItem("navy blue")]
        assert score_color_combination(items) == 1.0

    def test_empty_list_returns_one(self):
        assert score_color_combination([]) == 1.0

    def test_two_neutral_items(self):
        items = [FakeItem("black"), FakeItem("white")]
        assert score_color_combination(items) == SCORE_NEUTRAL

    def test_three_items_averages_pairs(self):
        # navy + white + black → all pairs involve a neutral → all 0.95
        items = [FakeItem("navy blue"), FakeItem("white"), FakeItem("black")]
        assert score_color_combination(items) == SCORE_NEUTRAL

    def test_considers_secondary_colors(self):
        # primary colors are both neutral (high score),
        # but secondary colors clash badly
        items = [
            FakeItem("white", secondary_color="red"),
            FakeItem("black", secondary_color="light purple"),
        ]
        score = score_color_combination(items)
        assert 0.0 <= score <= 1.0
        # Score should be pulled down by the red/light-purple clash
        assert score < SCORE_NEUTRAL

    def test_complementary_outfit_scores_high(self):
        items = [FakeItem("blue"), FakeItem("orange")]
        assert score_color_combination(items) == SCORE_COMPLEMENTARY

    def test_monochrome_outfit_scores_perfect(self):
        items = [FakeItem("navy blue"), FakeItem("navy blue"), FakeItem("navy blue")]
        assert score_color_combination(items) == SCORE_IDENTICAL
