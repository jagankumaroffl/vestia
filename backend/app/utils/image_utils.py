from __future__ import annotations
import os
import uuid
from pathlib import Path
from typing import Tuple

from fastapi import HTTPException, UploadFile
from PIL import Image

from app.config import settings

THUMBNAIL_SIZE = (400, 400)


def validate_image(file: UploadFile) -> None:
    """Raise HTTPException if file is not an allowed image type or too large."""
    if file.content_type not in settings.ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported image type '{file.content_type}'. "
                   f"Allowed: {settings.ALLOWED_MIME_TYPES}",
        )


async def save_upload(file: UploadFile, user_id: int) -> Tuple[str, str]:
    """
    Save uploaded image to disk.
    Returns (relative_path, absolute_path).
    """
    user_dir = Path(settings.UPLOAD_DIR) / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename or "image.jpg").suffix.lower() or ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    abs_path = user_dir / filename
    rel_path = f"{user_id}/{filename}"

    # Read and check size
    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)
    if size_mb > settings.MAX_IMAGE_SIZE_MB:
        raise HTTPException(
            status_code=413,
            detail=f"Image {size_mb:.1f} MB exceeds {settings.MAX_IMAGE_SIZE_MB} MB limit.",
        )

    abs_path.write_bytes(contents)

    # Create thumbnail for fast frontend loading
    _create_thumbnail(abs_path, user_dir / f"thumb_{filename}")

    return rel_path, str(abs_path)


def _create_thumbnail(src: Path, dst: Path) -> None:
    try:
        img = Image.open(src).convert("RGB")
        img.thumbnail(THUMBNAIL_SIZE, Image.LANCZOS)
        img.save(dst, optimize=True, quality=85)
    except Exception:
        pass  # thumbnail is best-effort; don't fail the upload


def get_absolute_path(relative_path: str) -> str:
    return str(Path(settings.UPLOAD_DIR) / relative_path)


def delete_image(relative_path: str) -> None:
    abs_path = Path(settings.UPLOAD_DIR) / relative_path
    if abs_path.exists():
        abs_path.unlink()
    # Also remove thumbnail if it exists
    thumb = abs_path.parent / f"thumb_{abs_path.name}"
    if thumb.exists():
        thumb.unlink()
