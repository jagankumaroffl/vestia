from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.config import settings
from app.services.wardrobe_service import WardrobeService
from app.schemas.clothing import ClothingItemResponse, ClothingItemUpdate

router = APIRouter()


@router.get("/wardrobe", response_model=List[ClothingItemResponse])
def list_wardrobe(
    category: Optional[str] = Query(None),
    style: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    color: Optional[str] = Query(None),
    pattern: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    service = WardrobeService(db)
    return service.list_items(
        user_id,
        category=category,
        style=style,
        season=season,
        color=color,
        pattern=pattern,
        skip=skip,
        limit=limit,
    )


# ── Static-path routes registered BEFORE /wardrobe/{item_id} ──────────────────
# FastAPI matches routes in registration order; without this, "/wardrobe/clusters"
# would be captured by the "/wardrobe/{item_id}" int path param and 422.

@router.get("/wardrobe/clusters", response_model=dict)
def get_wardrobe_clusters(
    n_clusters: int = Query(default=4, ge=2, le=10),
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
):
    """Group wardrobe into style clusters using FAISS K-Means."""
    from app.faiss.similarity_search import cluster_wardrobe
    return cluster_wardrobe(user_id, n_clusters=n_clusters)


@router.get("/wardrobe/{item_id}/similar", response_model=List[ClothingItemResponse])
def get_similar_items(
    item_id: int = Path(..., gt=0),
    k: int = Query(default=5, ge=1, le=20),
    user_id: int = Query(default=settings.DEFAULT_USER_ID),
    db: Session = Depends(get_db),
):
    """Return the k most visually similar wardrobe items using FAISS kNN."""
    from app.faiss.similarity_search import find_similar_items, embedding_from_json
    from app.database.repositories.clothing_repo import ClothingRepository

    repo = ClothingRepository(db)
    anchor = WardrobeService(db).get_item(item_id)
    embedding = embedding_from_json(anchor.embedding)

    if not embedding:
        return []

    similar = find_similar_items(user_id, embedding, k=k, exclude_item_id=item_id)
    results = []
    for s in similar:
        item = repo.get_by_id(s["item_id"])
        if item:
            results.append(item)
    return results


@router.get("/wardrobe/{item_id}", response_model=ClothingItemResponse)
def get_clothing_item(
    item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return WardrobeService(db).get_item(item_id)


@router.patch("/wardrobe/{item_id}", response_model=ClothingItemResponse)
def update_clothing_item(
    updates: ClothingItemUpdate,
    item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    return WardrobeService(db).update_item(item_id, updates)


@router.delete("/wardrobe/{item_id}", status_code=204)
def delete_clothing_item(
    item_id: int = Path(..., gt=0),
    db: Session = Depends(get_db),
):
    WardrobeService(db).delete_item(item_id)
