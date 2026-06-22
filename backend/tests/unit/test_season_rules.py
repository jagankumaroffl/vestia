"""Unit tests for season compatibility rules."""
from app.rules.season_rules import (
    score_season_pair,
    score_season_match,
    VALID_SEASONS,
    SCORE_ALL_SEASON,
)


class FakeItem:
    def __init__(self, season):
        self.season = season


class TestScoreSeasonPair:
    def test_all_season_item_matches_any_target(self):
        for target in VALID_SEASONS:
            assert score_season_pair("all_season", target) == SCORE_ALL_SEASON

    def test_all_season_target_matches_any_item(self):
        for item_season in VALID_SEASONS:
            assert score_season_pair(item_season, "all_season") == SCORE_ALL_SEASON

    def test_exact_match(self):
        assert score_season_pair("summer", "summer") == 1.0
        assert score_season_pair("winter", "winter") == 1.0
        assert score_season_pair("rainy", "rainy") == 1.0

    def test_summer_winter_mismatch_scores_low(self):
        score = score_season_pair("summer", "winter")
        assert score <= 0.2

    def test_winter_summer_symmetric(self):
        assert score_season_pair("summer", "winter") == score_season_pair("winter", "summer")

    def test_rainy_compatible_with_both(self):
        rainy_summer = score_season_pair("rainy", "summer")
        rainy_winter = score_season_pair("rainy", "winter")
        summer_winter = score_season_pair("summer", "winter")
        assert rainy_summer > summer_winter
        assert rainy_winter > summer_winter

    def test_case_insensitive(self):
        assert score_season_pair("Summer", "SUMMER") == 1.0

    def test_all_scores_in_range(self):
        for s1 in VALID_SEASONS:
            for s2 in VALID_SEASONS:
                score = score_season_pair(s1, s2)
                assert 0.0 <= score <= 1.0


class TestScoreSeasonMatch:
    def test_empty_items_returns_one(self):
        assert score_season_match([], "summer") == 1.0

    def test_all_matching_season(self):
        items = [FakeItem("summer"), FakeItem("summer"), FakeItem("all_season")]
        assert score_season_match(items, "summer") == 1.0

    def test_mismatched_season_lowers_score(self):
        items = [FakeItem("summer"), FakeItem("winter")]
        score = score_season_match(items, "summer")
        assert score < 1.0

    def test_all_season_items_always_score_perfect(self):
        items = [FakeItem("all_season"), FakeItem("all_season")]
        for target in VALID_SEASONS:
            assert score_season_match(items, target) == 1.0
