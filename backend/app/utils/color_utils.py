from __future__ import annotations
import colorsys
from typing import Optional, Tuple

# ── Named color → normalized key ─────────────────────────────────────────────
# Allows fuzzy matching from CV output to canonical names used in rules engine.

COLOR_ALIASES: dict[str, str] = {
    # Blues
    "navy": "navy blue", "dark blue": "navy blue", "marine": "navy blue",
    "sky blue": "light blue", "baby blue": "light blue",
    "royal blue": "blue", "cobalt": "blue",
    # Greys
    "gray": "grey", "charcoal": "dark grey", "silver": "light grey",
    # Whites / Blacks
    "off white": "white", "cream": "white", "ivory": "white",
    "jet black": "black", "onyx": "black",
    # Browns
    "tan": "beige", "khaki": "beige", "camel": "beige",
    "chocolate": "brown", "coffee": "brown",
    # Greens
    "olive": "olive green", "forest green": "dark green",
    "mint": "light green", "sage": "olive green",
    # Reds / Pinks
    "maroon": "burgundy", "wine": "burgundy", "crimson": "red",
    "rose": "pink", "blush": "pink",
    # Purples
    "violet": "purple", "lavender": "light purple",
    "mauve": "purple",
}

NEUTRAL_COLORS = {"black", "white", "grey", "dark grey", "light grey", "navy blue", "beige", "brown"}


def normalize_color(color: str) -> str:
    """Lowercase + alias resolution."""
    c = color.strip().lower()
    return COLOR_ALIASES.get(c, c)


def is_neutral(color: str) -> bool:
    return normalize_color(color) in NEUTRAL_COLORS


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    r, g, b = int(hex_color[0:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    return r, g, b


def rgb_to_hsl(r: int, g: int, b: int) -> Tuple[float, float, float]:
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    return h * 360, s * 100, l * 100


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return f"#{r:02x}{g:02x}{b:02x}"


def color_distance(color1: str, color2: str) -> float:
    """
    Simple hue-distance metric between two named colors.
    Returns 0.0 (identical) to 1.0 (opposite on hue wheel).
    Falls back to 0.5 if colors can't be parsed.
    """
    hue_map = {
        "red": 0, "orange": 30, "yellow": 60, "olive green": 80,
        "light green": 100, "dark green": 140, "green": 120,
        "light blue": 195, "blue": 210, "navy blue": 230,
        "purple": 270, "light purple": 290, "pink": 330,
        "burgundy": 345,
    }
    c1 = normalize_color(color1)
    c2 = normalize_color(color2)
    if c1 == c2:
        return 0.0
    if c1 not in hue_map or c2 not in hue_map:
        return 0.5
    diff = abs(hue_map[c1] - hue_map[c2])
    diff = min(diff, 360 - diff)   # take shorter arc
    return diff / 180.0            # normalise to [0, 1]
