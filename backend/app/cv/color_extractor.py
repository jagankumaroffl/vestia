"""
Color extraction using OpenCV K-Means clustering.

Pipeline:
  1. Remove near-white background pixels
  2. K-Means(k=5) on remaining pixel RGB values
  3. Map each cluster centroid to the closest named color
  4. Return primary and secondary colors by coverage
"""
from __future__ import annotations
from typing import List, Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.utils.color_utils import normalize_color

# ── Named color reference palette ────────────────────────────────────────────
# (canonical_name, (R, G, B)) — ordered from dark to light within hue families
COLOR_PALETTE: List[Tuple[str, Tuple[int, int, int]]] = [
    # Achromatic
    ("black",        (15,  15,  15)),
    ("dark grey",    (64,  64,  64)),
    ("grey",         (128, 128, 128)),
    ("light grey",   (192, 192, 192)),
    ("white",        (245, 245, 245)),
    # Blues
    ("navy blue",    (0,   0,   128)),
    ("blue",         (0,   90,  200)),
    ("light blue",   (135, 206, 235)),
    # Reds / Pinks
    ("burgundy",     (128, 0,   32)),
    ("red",          (200, 30,  30)),
    ("pink",         (255, 182, 193)),
    # Oranges / Yellows
    ("orange",       (255, 140, 0)),
    ("yellow",       (255, 215, 0)),
    # Greens
    ("dark green",   (0,   80,  0)),
    ("olive green",  (107, 142, 35)),
    ("green",        (0,   160, 0)),
    ("light green",  (144, 238, 144)),
    # Purples
    ("purple",       (128, 0,   128)),
    ("light purple", (200, 162, 200)),
    # Browns / Neutrals
    ("brown",        (101, 67,  33)),
    ("beige",        (245, 245, 220)),
]

_PALETTE_ARRAY = np.array([rgb for _, rgb in COLOR_PALETTE], dtype=np.float32)
_PALETTE_NAMES = [name for name, _ in COLOR_PALETTE]


def rgb_to_named_color(r: int, g: int, b: int) -> str:
    """
    Nearest-neighbour lookup in RGB space.
    Vectorised with numpy — fast even at large palette sizes.
    """
    query = np.array([[r, g, b]], dtype=np.float32)
    dists = np.linalg.norm(_PALETTE_ARRAY - query, axis=1)
    return _PALETTE_NAMES[int(np.argmin(dists))]


def extract_dominant_colors(
    image: Image.Image,
    k: int = 5,
    min_coverage: float = 0.05,
    max_pixels: int = 200 * 200,
) -> List[Tuple[str, float]]:
    """
    K-Means dominant color extraction.

    Returns sorted list of (color_name, coverage_fraction).
    Near-white background pixels are masked out before clustering.
    """
    img_array = np.array(image.convert("RGB"), dtype=np.float32)
    h, w = img_array.shape[:2]

    # Downsample for speed
    if h * w > max_pixels:
        scale = (max_pixels / (h * w)) ** 0.5
        new_h, new_w = max(1, int(h * scale)), max(1, int(w * scale))
        img_array = cv2.resize(img_array, (new_w, new_h))

    pixels = img_array.reshape(-1, 3)

    # Mask near-white background (all channels > 230)
    bg_mask = (pixels[:, 0] > 230) & (pixels[:, 1] > 230) & (pixels[:, 2] > 230)
    foreground = pixels[~bg_mask]

    if len(foreground) < k:
        # Fallback: use all pixels
        foreground = pixels

    k = min(k, len(foreground))

    # OpenCV K-Means — PP initialisation for stable centroids
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.2)
    _, labels, centers = cv2.kmeans(
        foreground.astype(np.float32),
        k, None,
        criteria,
        attempts=10,
        flags=cv2.KMEANS_PP_CENTERS,
    )

    counts = np.bincount(labels.flatten(), minlength=k)
    total = counts.sum()

    results: List[Tuple[str, float]] = []
    for i, center in enumerate(centers):
        coverage = counts[i] / total
        if coverage < min_coverage:
            continue
        r, g, b = int(center[0]), int(center[1]), int(center[2])
        name = rgb_to_named_color(r, g, b)
        results.append((name, round(float(coverage), 3)))

    results.sort(key=lambda x: x[1], reverse=True)
    return results


def get_primary_secondary(
    image: Image.Image,
) -> Tuple[str, Optional[str]]:
    """
    Returns (primary_color, secondary_color | None).

    Secondary is suppressed when:
      - Primary dominates > 80% of pixels, or
      - Secondary resolves to the same named color as primary.
    """
    dominant = extract_dominant_colors(image)

    if not dominant:
        return "unknown", None

    primary_raw, primary_cov = dominant[0]
    primary = normalize_color(primary_raw)

    if primary_cov > 0.80 or len(dominant) < 2:
        return primary, None

    # Walk down the list to find a distinct secondary
    secondary = None
    for name, _ in dominant[1:]:
        candidate = normalize_color(name)
        if candidate != primary:
            secondary = candidate
            break

    return primary, secondary
