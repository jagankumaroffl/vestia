"""
Phase 2 stub — kept as fallback when FashionCLIP model is unavailable
(e.g. CI environment, first-run before model download).
"""
from __future__ import annotations
import json
import random

_STUB_CATEGORIES = ["topwear", "bottomwear", "footwear", "accessory", "outerwear"]
_STUB_SUBCATS = {
    "topwear":   ["t-shirt", "polo", "oxford shirt", "casual shirt", "hoodie", "sweater"],
    "bottomwear":["jeans", "chinos", "formal trousers", "shorts", "joggers"],
    "footwear":  ["sneakers", "formal shoes", "loafers", "boots", "sandals"],
    "accessory": ["watch", "belt", "sunglasses", "cap", "bag"],
    "outerwear": ["blazer", "jacket", "overcoat"],
}
_STUB_COLORS  = ["navy blue", "white", "black", "grey", "beige", "light blue", "olive green", "burgundy"]
_STUB_PATTERNS = ["solid", "striped", "checked", "printed"]
_STUB_STYLES   = ["casual", "formal", "business_casual", "smart_casual"]
_STUB_SEASONS  = ["summer", "winter", "all_season"]


def analyze_image(image_path: str) -> dict:
    """Deterministic-ish stub — replaced by real pipeline in production."""
    cat = random.choice(_STUB_CATEGORIES)
    return {
        "category":        cat,
        "subcategory":     random.choice(_STUB_SUBCATS[cat]),
        "primary_color":   random.choice(_STUB_COLORS),
        "secondary_color": random.choice([None] + _STUB_COLORS),
        "pattern":         random.choice(_STUB_PATTERNS),
        "style":           random.choice(_STUB_STYLES),
        "season":          random.choice(_STUB_SEASONS),
        "gender":          "unisex",
        "embedding":       json.dumps([0.0] * 512),
        "confidence":      0.45,   # always flags for user review
    }
