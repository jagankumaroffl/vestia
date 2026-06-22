"""Unit tests for style compatibility rules."""
from app.rules.style_rules import (
    score_style_pair,
    score_style_combination,
    SCORE_SAME_STYLE,
    VALID_STYLES,
)


class FakeItem:
    def __init__(self, style):
        self.style = style


class TestScoreStylePair:
    def test_same_style_scores_perfect(self):
        for style in VALID_STYLES:
            assert score_style_pair(style, style) == SCORE_SAME_STYLE

    def test_symmetric(self):
        assert score_style_pair("casual", "formal") == score_style_pair("formal", "casual")

    def test_casual_formal_low_compat(self):
        score = score_style_pair("casual", "formal")
        assert score < 0.3

    def test_business_casual_smart_casual_high_compat(self):
        score = score_style_pair("business_casual", "smart_casual")
        assert score >= 0.8

    def test_casual_sports_high_compat(self):
        score = score_style_pair("casual", "sports")
        assert score >= 0.8

    def test_formal_sports_very_low(self):
        score = score_style_pair("formal", "sports")
        assert score <= 0.1

    def test_all_pairs_in_range(self):
        for s1 in VALID_STYLES:
            for s2 in VALID_STYLES:
                score = score_style_pair(s1, s2)
                assert 0.0 <= score <= 1.0

    def test_case_insensitive(self):
        assert score_style_pair("Casual", "CASUAL") == SCORE_SAME_STYLE


class TestScoreStyleCombination:
    def test_single_item_returns_one(self):
        assert score_style_combination([FakeItem("casual")]) == 1.0

    def test_empty_returns_one(self):
        assert score_style_combination([]) == 1.0

    def test_all_same_style(self):
        items = [FakeItem("formal"), FakeItem("formal"), FakeItem("formal")]
        assert score_style_combination(items) == 1.0

    def test_mixed_styles_averages(self):
        items = [FakeItem("casual"), FakeItem("formal")]
        score = score_style_combination(items)
        assert score == score_style_pair("casual", "formal")

    def test_three_items_average_of_three_pairs(self):
        items = [FakeItem("casual"), FakeItem("smart_casual"), FakeItem("sports")]
        expected = round((
            score_style_pair("casual", "smart_casual") +
            score_style_pair("casual", "sports") +
            score_style_pair("smart_casual", "sports")
        ) / 3, 4)
        assert score_style_combination(items) == expected
