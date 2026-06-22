"""Unit tests for repetition avoidance rules."""
from app.rules.repetition_rules import score_repetition, HEAVY_PENALTY


class FakeItem:
    def __init__(self, item_id, category):
        self.id = item_id
        self.category = category


class TestScoreRepetition:
    def test_no_recently_worn_returns_one(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear")]
        assert score_repetition(items, set()) == 1.0

    def test_no_overlap_returns_one(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear")]
        assert score_repetition(items, {99, 100}) == 1.0

    def test_repeated_topwear_penalized(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear")]
        score = score_repetition(items, {1})
        assert score == round(1.0 - HEAVY_PENALTY, 4)

    def test_repeated_bottomwear_penalized(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear")]
        score = score_repetition(items, {2})
        assert score == round(1.0 - HEAVY_PENALTY, 4)

    def test_both_top_and_bottom_repeated(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear")]
        score = score_repetition(items, {1, 2})
        assert score == round(1.0 - 2 * HEAVY_PENALTY, 4)

    def test_repeated_footwear_not_penalized(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear"), FakeItem(3, "footwear")]
        score = score_repetition(items, {3})
        assert score == 1.0

    def test_repeated_accessory_not_penalized(self):
        items = [FakeItem(1, "topwear"), FakeItem(2, "bottomwear"), FakeItem(4, "accessory")]
        score = score_repetition(items, {4})
        assert score == 1.0

    def test_repeated_outerwear_not_penalized(self):
        items = [FakeItem(1, "topwear"), FakeItem(5, "outerwear")]
        score = score_repetition(items, {5})
        assert score == 1.0

    def test_score_never_negative(self):
        items = [FakeItem(i, "topwear") for i in range(1, 6)]
        score = score_repetition(items, set(range(1, 6)))
        assert score == 0.0
