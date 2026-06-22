"""
Style compatibility rules.

Defines a symmetric compatibility matrix between the 7 supported styles:
  casual, formal, business_casual, smart_casual, party, sports, ethnic

score_style_pair() returns 0.0–1.0 for any two styles.
score_style_combination() averages pairwise scores across all items.
"""
from __future__ import annotations
import itertools
from typing import List

VALID_STYLES = {
    "casual", "formal", "business_casual",
    "smart_casual", "party", "sports", "ethnic",
}

# ── Symmetric compatibility matrix ────────────────────────────────────────────
# Keys are unordered pairs (frozenset). Same-style pairs are always 1.0
# and handled separately — not listed here.
_STYLE_COMPAT: dict[frozenset[str], float] = {
    frozenset({"casual", "smart_casual"}):        0.85,
    frozenset({"casual", "business_casual"}):     0.50,
    frozenset({"casual", "formal"}):               0.15,
    frozenset({"casual", "party"}):                0.55,
    frozenset({"casual", "sports"}):               0.90,
    frozenset({"casual", "ethnic"}):               0.40,

    frozenset({"formal", "business_casual"}):     0.70,
    frozenset({"formal", "smart_casual"}):        0.50,
    frozenset({"formal", "party"}):                0.60,
    frozenset({"formal", "sports"}):               0.05,
    frozenset({"formal", "ethnic"}):               0.45,

    frozenset({"business_casual", "smart_casual"}): 0.85,
    frozenset({"business_casual", "party"}):        0.45,
    frozenset({"business_casual", "sports"}):       0.20,
    frozenset({"business_casual", "ethnic"}):       0.40,

    frozenset({"smart_casual", "party"}):          0.75,
    frozenset({"smart_casual", "sports"}):         0.40,
    frozenset({"smart_casual", "ethnic"}):         0.50,

    frozenset({"party", "sports"}):                0.15,
    frozenset({"party", "ethnic"}):                0.50,

    frozenset({"sports", "ethnic"}):               0.15,
}

# Fallback for any pair not explicitly listed (shouldn't happen with VALID_STYLES)
_DEFAULT_COMPAT = 0.35

SCORE_SAME_STYLE = 1.0


def score_style_pair(style1: str, style2: str) -> float:
    """
    Compatibility score between two styles, 0.0 (clash) – 1.0 (perfect match).
    Same style on both items always scores 1.0.
    """
    s1, s2 = style1.strip().lower(), style2.strip().lower()
    if s1 == s2:
        return SCORE_SAME_STYLE

    pair = frozenset({s1, s2})
    return _STYLE_COMPAT.get(pair, _DEFAULT_COMPAT)


def score_style_combination(items: List) -> float:
    """
    Average pairwise style compatibility across all items in an outfit.
    Returns 1.0 for single-item outfits (nothing to compare).
    """
    styles = [item.style for item in items if getattr(item, "style", None)]

    if len(styles) < 2:
        return 1.0

    pairs = list(itertools.combinations(styles, 2))
    scores = [score_style_pair(s1, s2) for s1, s2 in pairs]
    return round(sum(scores) / len(scores), 4)
