"""
Scoring engine — combines all rule modules into a single deterministic score.

  total_score = color_score      * 0.35
              + style_score       * 0.30
              + occasion_score    * 0.20
              + season_score       * 0.10
              + repetition_score   * 0.05

No AI / LLM involved — every score is computed from explicit rule tables
in color_rules, style_rules, occasion_rules, season_rules, repetition_rules.
"""
from __future__ import annotations
from typing import List, Set

from app.rules.color_rules import score_color_combination
from app.rules.style_rules import score_style_combination
from app.rules.occasion_rules import score_occasion_match
from app.rules.season_rules import score_season_match
from app.rules.repetition_rules import score_repetition

# ── Weights — must sum to 1.0 ─────────────────────────────────────────────────
WEIGHT_COLOR      = 0.35
WEIGHT_STYLE      = 0.30
WEIGHT_OCCASION   = 0.20
WEIGHT_SEASON     = 0.10
WEIGHT_REPETITION = 0.05

assert abs(
    WEIGHT_COLOR + WEIGHT_STYLE + WEIGHT_OCCASION + WEIGHT_SEASON + WEIGHT_REPETITION - 1.0
) < 1e-9, "Scoring weights must sum to 1.0"


def score_combination(
    items: List,
    occasion: str,
    season: str,
    recently_worn_ids: Set[int],
) -> dict:
    """
    Score a candidate outfit (list of ClothingItem ORM objects).

    Returns dict with keys:
        total_score, color_score, style_score,
        occasion_score, season_score, repetition_score
    All values are floats in [0.0, 1.0].
    """
    color_score      = score_color_combination(items)
    style_score      = score_style_combination(items)
    occasion_score   = score_occasion_match(items, occasion)
    season_score     = score_season_match(items, season)
    repetition_score = score_repetition(items, recently_worn_ids)

    total_score = round(
        color_score      * WEIGHT_COLOR +
        style_score      * WEIGHT_STYLE +
        occasion_score   * WEIGHT_OCCASION +
        season_score     * WEIGHT_SEASON +
        repetition_score * WEIGHT_REPETITION,
        4,
    )

    return {
        "total_score":      total_score,
        "color_score":      color_score,
        "style_score":      style_score,
        "occasion_score":   occasion_score,
        "season_score":     season_score,
        "repetition_score": repetition_score,
    }
