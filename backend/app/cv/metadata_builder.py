"""
Metadata builder.

Orchestrates the full CV pipeline for a single image:
  1. Load + preprocess
  2. FashionCLIP classification + embedding
  3. OpenCV colour extraction
  4. Merge into the canonical metadata dict

This is the only module pipeline.py imports.
"""
from __future__ import annotations

import json
import logging
from functools import lru_cache

from PIL import Image

from app.cv.image_processor import load_and_preprocess
from app.cv.fashion_clip import FashionCLIPAnalyzer
from app.cv.color_extractor import get_primary_secondary

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _get_analyzer() -> FashionCLIPAnalyzer:
    return FashionCLIPAnalyzer()


def build_metadata(image_path: str) -> dict:
    """
    Full pipeline entry point.

    Returns a dict matching the Phase 2 contract:
      category, subcategory, primary_color, secondary_color,
      pattern, style, season, gender, embedding (JSON str), confidence
    """
    # ── 1. Preprocess ─────────────────────────────────────────────────────────
    image: Image.Image = load_and_preprocess(image_path)
    logger.debug("Image preprocessed: %s", image_path)

    # ── 2. FashionCLIP classification + embedding ────────────────────────────
    analyzer = _get_analyzer()
    clip_result = analyzer.analyze(image)
    logger.debug("CLIP result: %s (conf=%.2f)", clip_result["category"], clip_result["confidence"])

    # ── 3. Colour extraction ──────────────────────────────────────────────────
    primary_color, secondary_color = get_primary_secondary(image)
    logger.debug("Colours: primary=%s secondary=%s", primary_color, secondary_color)

    # ── 4. Assemble final metadata ────────────────────────────────────────────
    return {
        "category":        clip_result["category"],
        "subcategory":     clip_result["subcategory"],
        "primary_color":   primary_color,
        "secondary_color": secondary_color,
        "pattern":         clip_result["pattern"],
        "style":           clip_result["style"],
        "season":          clip_result["season"],
        "gender":          clip_result["gender"],
        "embedding":       json.dumps(clip_result["embedding"]),
        "confidence":      clip_result["confidence"],
    }
