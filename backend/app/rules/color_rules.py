"""
Color matching rules.

Implements:
  - Complementary color pairs (opposite on color wheel)
  - Analogous color pairs (adjacent on color wheel)
  - Neutral color handling (matches almost everything)

score_color_pair() returns 0.0–1.0 for any two named colors.
score_color_combination() averages pairwise scores across all items
in an outfit (using primary + secondary colors).
"""
from __future__ import annotations
import itertools
from typing import List

from app.utils.color_utils import normalize_color, is_neutral, color_distance


# ── Explicit complementary pairs (color-wheel opposites) ─────────────────────
COMPLEMENTARY_PAIRS: set[frozenset[str]] = {
    frozenset({"blue", "orange"}),
    frozenset({"navy blue", "orange"}),
    frozenset({"light blue", "orange"}),
    frozenset({"purple", "yellow"}),
    frozenset({"light purple", "yellow"}),
    frozenset({"red", "green"}),
    frozenset({"burgundy", "green"}),
    frozenset({"red", "dark green"}),
}

# ── Explicit analogous pairs (adjacent on color wheel) ────────────────────────
ANALOGOUS_PAIRS: set[frozenset[str]] = {
    frozenset({"blue", "light green"}),
    frozenset({"blue", "light blue"}),
    frozenset({"navy blue", "light green"}),
    frozenset({"blue", "purple"}),
    frozenset({"light blue", "light purple"}),
    frozenset({"navy blue", "purple"}),
    frozenset({"green", "light green"}),
    frozenset({"green", "olive green"}),
    frozenset({"olive green", "beige"}),
    frozenset({"orange", "yellow"}),
    frozenset({"red", "orange"}),
    frozenset({"red", "burgundy"}),
    frozenset({"purple", "pink"}),
    frozenset({"pink", "burgundy"}),
    frozenset({"pink", "red"}),
}

# Score constants
SCORE_IDENTICAL     = 1.00   # same color — always safe
SCORE_NEUTRAL       = 0.95   # one or both colors neutral — matches almost anything
SCORE_COMPLEMENTARY = 1.00   # intentional color-theory pairing
SCORE_ANALOGOUS     = 0.85   # harmonious adjacent hues
SCORE_CLASH_FLOOR   = 0.30   # worst-case for unrelated mid-distance hues


def score_color_pair(color1: str, color2: str) -> float:
    """
    Score how well two named colors work together, 0.0 (clash) – 1.0 (ideal).

    Priority order:
      1. Identical colors            → 1.00
      2. Either color is neutral     → 0.95
      3. Known complementary pair    → 1.00
      4. Known analogous pair        → 0.85
      5. Fallback: hue-distance based scoring
    """
    c1 = normalize_color(color1)
    c2 = normalize_color(color2)

    if c1 == c2:
        return SCORE_IDENTICAL

    if is_neutral(c1) or is_neutral(c2):
        return SCORE_NEUTRAL

    pair = frozenset({c1, c2})
    if pair in COMPLEMENTARY_PAIRS:
        return SCORE_COMPLEMENTARY
    if pair in ANALOGOUS_PAIRS:
        return SCORE_ANALOGOUS

    # Fallback: hue-distance heuristic.
    # dist ∈ [0,1] where 0 = same hue, 1 = opposite hue.
    dist = color_distance(c1, c2)

    if dist <= 0.15:
        # Very close hues — near-analogous, generally pleasant
        return 0.80
    if dist >= 0.85:
        # Near-opposite hues — near-complementary, generally bold but workable
        return 0.75
    # Mid-range hue difference — most likely to clash
    return max(SCORE_CLASH_FLOOR, 1.0 - dist)


def score_color_combination(items: List) -> float:
    """
    Average pairwise color score across all clothing items in an outfit.

    Considers both primary_color and secondary_color (when present) so
    a patterned item's accent color is factored into harmony scoring.

    Returns 1.0 for outfits with fewer than 2 colors total (nothing to clash).
    """
    colors: List[str] = []
    for item in items:
        if item.primary_color:
            colors.append(item.primary_color)
        if getattr(item, "secondary_color", None):
            colors.append(item.secondary_color)

    if len(colors) < 2:
        return 1.0

    pairs = list(itertools.combinations(colors, 2))
    scores = [score_color_pair(c1, c2) for c1, c2 in pairs]
    return round(sum(scores) / len(scores), 4)
