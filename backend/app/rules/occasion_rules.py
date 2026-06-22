"""
Occasion rules.

Defines, for each of the 9 supported occasions:
  - required_categories : clothing categories every outfit MUST include
  - optional_categories : categories that may be included (outerwear, accessories)
  - preferred_styles    : ordered best→worst style fit for occasion_score

score_occasion_match() rewards items whose `style` aligns with the
occasion's preferred styles.
"""
from __future__ import annotations
from typing import List

# ── Category → outfit position (shared with outfit_service) ──────────────────
CATEGORY_TO_POSITION: dict[str, str] = {
    "topwear":    "top",
    "bottomwear": "bottom",
    "footwear":   "shoes",
    "outerwear":  "outerwear",
    "accessory":  "accessory",
}

# ── Occasion definitions ───────────────────────────────────────────────────────
OCCASION_RULES: dict[str, dict] = {
    "casual": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["accessory"],
        "preferred_styles": ["casual", "smart_casual", "sports"],
    },
    "college": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["accessory"],
        "preferred_styles": ["casual", "smart_casual"],
    },
    "office": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["outerwear", "accessory"],
        "preferred_styles": ["business_casual", "smart_casual", "formal"],
    },
    "business_meeting": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["outerwear", "accessory"],
        "preferred_styles": ["formal", "business_casual"],
    },
    "formal_event": {
        "required_categories": ["topwear", "bottomwear", "footwear", "outerwear"],
        "optional_categories": ["accessory"],
        "preferred_styles": ["formal"],
    },
    "party": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["accessory"],
        "preferred_styles": ["party", "smart_casual"],
    },
    "date_night": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["accessory"],
        "preferred_styles": ["smart_casual", "party"],
    },
    "wedding": {
        "required_categories": ["topwear", "bottomwear", "footwear", "outerwear"],
        "optional_categories": ["accessory"],
        "preferred_styles": ["formal", "ethnic", "party"],
    },
    "travel": {
        "required_categories": ["topwear", "bottomwear", "footwear"],
        "optional_categories": ["outerwear", "accessory"],
        "preferred_styles": ["casual", "sports", "smart_casual"],
    },
}

VALID_OCCASIONS = set(OCCASION_RULES.keys())

# Score given to an item style that's not in the occasion's preferred list at all
SCORE_UNLISTED_STYLE = 0.20
# Decay applied per rank position down the preferred_styles list
RANK_DECAY = 0.20


def get_required_categories(occasion: str) -> List[str]:
    rules = OCCASION_RULES.get(occasion)
    return rules["required_categories"] if rules else ["topwear", "bottomwear", "footwear"]


def get_optional_categories(occasion: str) -> List[str]:
    rules = OCCASION_RULES.get(occasion)
    return rules["optional_categories"] if rules else []


def score_style_for_occasion(style: str, occasion: str) -> float:
    """
    Score a single item's style against an occasion's preferred style list.

    Best-ranked preferred style → 1.0
    Each subsequent rank        → -0.20
    Style not in the list at all → SCORE_UNLISTED_STYLE
    """
    rules = OCCASION_RULES.get(occasion)
    if not rules:
        return 0.5  # unknown occasion — neutral score

    preferred = rules["preferred_styles"]
    if style not in preferred:
        return SCORE_UNLISTED_STYLE

    rank = preferred.index(style)
    return max(0.2, 1.0 - rank * RANK_DECAY)


def score_occasion_match(items: List, occasion: str) -> float:
    """
    Average per-item occasion-style fit, plus a structural bonus/penalty
    for satisfying the occasion's required_categories.

    Returns 0.0–1.0.
    """
    rules = OCCASION_RULES.get(occasion)
    if not rules:
        return 0.5

    if not items:
        return 0.0

    # Per-item style fit
    style_scores = [score_style_for_occasion(item.style, occasion) for item in items]
    avg_style = sum(style_scores) / len(style_scores)

    # Structural check: are all required categories present?
    present_categories = {item.category for item in items}
    required = set(rules["required_categories"])
    missing = required - present_categories

    if missing:
        # Heavy penalty — outfit is structurally incomplete for this occasion
        structural_score = max(0.0, 1.0 - 0.5 * len(missing))
    else:
        structural_score = 1.0

    # Weighted combination: structure matters more than style-rank nuance
    return round(0.5 * structural_score + 0.5 * avg_style, 4)
