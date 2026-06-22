"""
Season compatibility rules.

Each clothing item has a `season` of: summer | winter | rainy | all_season
The outfit is generated for a target `season`.

score_season_pair() returns how well an item's season fits the target.
score_season_match() averages across all items in the outfit.
"""
from __future__ import annotations
from typing import List

VALID_SEASONS = {"summer", "winter", "rainy", "all_season"}

# ── Compatibility matrix (item_season → target_season → score) ───────────────
# all_season items always score 1.0 regardless of target (handled separately).
_SEASON_COMPAT: dict[str, dict[str, float]] = {
    "summer": {
        "summer": 1.0,
        "winter": 0.10,
        "rainy":  0.40,
    },
    "winter": {
        "summer": 0.10,
        "winter": 1.0,
        "rainy":  0.50,
    },
    "rainy": {
        "summer": 0.40,
        "winter": 0.50,
        "rainy":  1.0,
    },
}

SCORE_ALL_SEASON = 1.0


def score_season_pair(item_season: str, target_season: str) -> float:
    """
    Score how well a single item's season fits the target season, 0.0–1.0.

    - 'all_season' on either side always scores 1.0.
    - Exact match scores 1.0.
    - Otherwise looked up from the compatibility matrix.
    """
    item_s = item_season.strip().lower()
    target_s = target_season.strip().lower()

    if item_s == "all_season" or target_s == "all_season":
        return SCORE_ALL_SEASON

    if item_s == target_s:
        return 1.0

    return _SEASON_COMPAT.get(item_s, {}).get(target_s, 0.5)


def score_season_match(items: List, target_season: str) -> float:
    """
    Average season-fit score across all items in an outfit.
    Returns 1.0 for an empty item list (nothing to penalise).
    """
    if not items:
        return 1.0

    scores = [score_season_pair(item.season, target_season) for item in items]
    return round(sum(scores) / len(scores), 4)
