"""
Image preprocessing before CV pipeline inference.
All inputs are normalised here so FashionCLIP and OpenCV
both receive a clean, square, RGB image.
"""
from __future__ import annotations
from PIL import Image, ImageOps

# FashionCLIP expects at least 224×224; we pad to 512 for colour accuracy
TARGET_SIZE = (512, 512)


def load_and_preprocess(image_path: str) -> Image.Image:
    """
    Load image from disk, correct EXIF rotation, convert to RGB,
    resize preserving aspect ratio, and pad to TARGET_SIZE square.
    """
    img = Image.open(image_path)
    img = ImageOps.exif_transpose(img)      # correct camera rotation
    img = img.convert("RGB")               # handles RGBA, P, L, CMYK
    img = _pad_to_square(img, TARGET_SIZE)
    return img


def _pad_to_square(img: Image.Image, target: tuple[int, int]) -> Image.Image:
    """
    Resize to fit within target keeping aspect ratio,
    then centre-paste on a white background.
    """
    img.thumbnail(target, Image.LANCZOS)
    background = Image.new("RGB", target, (255, 255, 255))
    offset_x = (target[0] - img.width) // 2
    offset_y = (target[1] - img.height) // 2
    background.paste(img, (offset_x, offset_y))
    return background


def crop_center_region(img: Image.Image, fraction: float = 0.7) -> Image.Image:
    """
    Crop the central fraction of an image.
    Used to reduce background noise when extracting colours.
    """
    w, h = img.size
    margin_x = int(w * (1 - fraction) / 2)
    margin_y = int(h * (1 - fraction) / 2)
    return img.crop((margin_x, margin_y, w - margin_x, h - margin_y))
