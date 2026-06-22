from __future__ import annotations
import json
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, UploadFile, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.config import settings
from app.utils.image_utils import validate_image, save_upload
from app.cv.pipeline import analyze_image
from app.services.wardrobe_service import WardrobeService
from app.schemas.recommendation import UploadAnalysisResult
from app.schemas.clothing import ClothingItemCreate
from app.faiss.index_manager import add_embedding
from app.faiss.similarity_search import find_duplicates, embedding_from_json

router = APIRouter()


@router.post("/upload", response_model=UploadAnalysisResult, status_code=201)
async def upload_clothing_image(
    file: UploadFile = File(..., description="JPEG / PNG / WebP clothing image"),
    category: Optional[str] = Form(None),
    subcategory: Optional[str] = Form(None),
    style: Optional[str] = Form(None),
    season: Optional[str] = Form(None),
    tags: Optional[str] = Form(None, description="Comma-separated tag list"),
    user_id: int = Form(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    """
    Upload → CV analysis → DB save → FAISS index.

    Steps:
      1. Validate MIME type + size.
      2. Save image to disk.
      3. Run CV pipeline (FashionCLIP + OpenCV colour extraction).
      4. Merge with optional user overrides.
      5. Persist ClothingItem to SQLite.
      6. Add embedding to user's FAISS index.
      7. Check for potential duplicates.
      8. Return analysis result with confidence + duplicate warning.
    """
    # 1. Validate
    validate_image(file)

    # 2. Save
    rel_path, abs_path = await save_upload(file, user_id)

    # 3. CV analysis
    cv_result = analyze_image(abs_path)

    # 4. User overrides
    overrides = None
    if any([category, subcategory, style, season, tags]):
        overrides = ClothingItemCreate(
            category=category or cv_result["category"],
            subcategory=subcategory or cv_result["subcategory"],
            primary_color=cv_result["primary_color"],
            style=style or cv_result["style"],
            season=season or cv_result["season"],
            tags=[t.strip() for t in tags.split(",")] if tags else [],
        )

    # 5. Persist
    service = WardrobeService(db)
    item = service.add_item(user_id, rel_path, cv_result, overrides)

    # 6. FAISS index
    embedding = embedding_from_json(cv_result.get("embedding"))
    duplicate_ids: list[int] = []
    if embedding:
        duplicates = find_duplicates(user_id, embedding, exclude_item_id=item.id)
        duplicate_ids = [d["item_id"] for d in duplicates]
        add_embedding(user_id, item.id, embedding)

    return UploadAnalysisResult(
        clothing_item_id=item.id,
        image_path=item.image_path,
        category=item.category,
        subcategory=item.subcategory,
        primary_color=item.primary_color,
        secondary_color=item.secondary_color,
        pattern=item.pattern,
        style=item.style,
        season=item.season,
        gender=item.gender,
        confidence=cv_result.get("confidence", 0.55),
        needs_review=cv_result.get("confidence", 0.55) < 0.6,
    )
