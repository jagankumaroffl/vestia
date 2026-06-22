"""
Repetition avoidance rules.

Per project spec:
  - If a TOP was worn yesterday      → heavy penalty
  - If BOTTOMS were worn yesterday   → heavy penalty
  - Accessories, footwear, outerwear → may be reused freely (no penalty)

score_repetition() returns 1.0 (no repeats) down to 0.0 (both top and
bottom were worn in the lookback window).
"""
from __future__ import annotations
from typing import List, Set

# Categories subject to the heavy repetition penalty
PENALIZED_CATEGORIES = {"topwear", "bottomwear"}

# Penalty applied per repeated topwear/bottomwear item
HEAVY_PENALTY = 0.50


def score_repetition(items: List, recently_worn_ids: Set[int]) -> float:
    """
    Score outfit variety relative to recently worn items.

    Only topwear and bottomwear items count toward the penalty.
    Footwear, outerwear, and accessories are exempt — they may repeat
    on consecutive days without affecting this score.

    Returns max(0.0, 1.0 - HEAVY_PENALTY * num_repeated_top_or_bottom).
    """
    if not recently_worn_ids:
        return 1.0

    repeats = sum(
        1 for item in items
        if item.category in PENALIZED_CATEGORIES and item.id in recently_worn_ids
    )

    return round(max(0.0, 1.0 - HEAVY_PENALTY * repeats), 4)
