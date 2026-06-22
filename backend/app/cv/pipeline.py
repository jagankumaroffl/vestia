"""
CV pipeline entry point.

Replaces the Phase 2 stub with real FashionCLIP + OpenCV inference.
Falls back gracefully to _stub.py if the model is not yet downloaded
or torch is unavailable (useful in CI / lightweight environments).
"""
from __future__ import annotations
import logging

logger = logging.getLogger(__name__)


def analyze_image(image_path: str) -> dict:
    """
    Run full CV analysis on a clothing image.

    Returns metadata dict:
        category, subcategory, primary_color, secondary_color,
        pattern, style, season, gender, embedding (JSON str), confidence

    Confidence < 0.6 sets needs_review=True in the upload router.
    """
    try:
        from app.cv.metadata_builder import build_metadata
        return build_metadata(image_path)
    except ImportError:
        logger.warning("torch/transformers not installed — using stub pipeline.")
        from app.cv._stub import analyze_image as _stub
        return _stub(image_path)
    except Exception as exc:
        logger.error("CV pipeline failed for %s: %s. Falling back to stub.", image_path, exc)
        from app.cv._stub import analyze_image as _stub
        return _stub(image_path)
