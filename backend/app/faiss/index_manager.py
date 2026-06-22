"""
FAISS index manager.

One index per user, stored at:
  data/faiss_index/{user_id}.index          — FAISS binary
  data/faiss_index/{user_id}_mapping.json   — item_id list aligned with FAISS row positions

The mapping file lets us convert FAISS result positions → clothing item IDs.

Embedding dimension: 512 (FashionCLIP output).
Index type: IndexFlatL2 — exact L2 search.
  Upgrade to IndexIVFFlat for wardrobe sizes > 10,000 items.
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import List, Optional

import numpy as np

from app.config import settings

logger = logging.getLogger(__name__)

DIM = settings.EMBEDDING_DIMENSION   # 512

try:
    import faiss
    _FAISS_AVAILABLE = True
except ImportError:
    _FAISS_AVAILABLE = False
    logger.warning("faiss-cpu not installed. FAISS features disabled.")


def _index_path(user_id: int) -> Path:
    return Path(settings.FAISS_INDEX_DIR) / f"{user_id}.index"


def _mapping_path(user_id: int) -> Path:
    return Path(settings.FAISS_INDEX_DIR) / f"{user_id}_mapping.json"


# ── Load / save ───────────────────────────────────────────────────────────────

def load_index(user_id: int):
    """Load existing FAISS index from disk. Returns (index, id_list) or (None, [])."""
    if not _FAISS_AVAILABLE:
        return None, []

    idx_path = _index_path(user_id)
    map_path = _mapping_path(user_id)

    if not idx_path.exists() or not map_path.exists():
        return None, []

    try:
        index = faiss.read_index(str(idx_path))
        item_ids: List[int] = json.loads(map_path.read_text())
        logger.debug("Loaded FAISS index for user %d — %d vectors", user_id, index.ntotal)
        return index, item_ids
    except Exception as exc:
        logger.error("Failed to load FAISS index for user %d: %s", user_id, exc)
        return None, []


def save_index(user_id: int, index, item_ids: List[int]) -> None:
    """Persist FAISS index and ID mapping to disk."""
    if not _FAISS_AVAILABLE or index is None:
        return

    os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)
    faiss.write_index(index, str(_index_path(user_id)))
    _mapping_path(user_id).write_text(json.dumps(item_ids))
    logger.debug("Saved FAISS index for user %d — %d vectors", user_id, index.ntotal)


def _new_index():
    """Create a fresh flat L2 index."""
    return faiss.IndexFlatL2(DIM)


# ── Public API ────────────────────────────────────────────────────────────────

def add_embedding(user_id: int, item_id: int, embedding: List[float]) -> None:
    """
    Add a single clothing item embedding to the user's FAISS index.
    Creates the index if it doesn't exist yet.
    """
    if not _FAISS_AVAILABLE:
        return

    index, item_ids = load_index(user_id)
    if index is None:
        index = _new_index()

    vec = np.array([embedding], dtype=np.float32)
    index.add(vec)
    item_ids.append(item_id)
    save_index(user_id, index, item_ids)
    logger.debug("Added embedding for item %d → user %d index", item_id, user_id)


def remove_embedding(user_id: int, item_id: int) -> None:
    """
    Remove an item embedding by rebuilding the index without it.
    O(n) — acceptable for typical wardrobe sizes (<1000 items).
    """
    if not _FAISS_AVAILABLE:
        return

    index, item_ids = load_index(user_id)
    if index is None or item_id not in item_ids:
        return

    # Reconstruct index minus the removed item
    all_vecs = index.reconstruct_n(0, index.ntotal)
    keep_positions = [i for i, iid in enumerate(item_ids) if iid != item_id]

    new_index = _new_index()
    if keep_positions:
        new_vecs = all_vecs[keep_positions]
        new_index.add(new_vecs)

    new_ids = [item_ids[i] for i in keep_positions]
    save_index(user_id, new_index, new_ids)


def rebuild_index(user_id: int, embeddings: dict[int, List[float]]) -> None:
    """
    Full rebuild from a {item_id: embedding} dict.
    Used for bulk re-indexing after batch uploads.
    """
    if not _FAISS_AVAILABLE or not embeddings:
        return

    index = _new_index()
    item_ids: List[int] = list(embeddings.keys())
    vecs = np.array([embeddings[iid] for iid in item_ids], dtype=np.float32)
    index.add(vecs)
    save_index(user_id, index, item_ids)
    logger.info("Rebuilt FAISS index for user %d — %d vectors", user_id, len(item_ids))


def index_size(user_id: int) -> int:
    """Return number of vectors in the user's index."""
    if not _FAISS_AVAILABLE:
        return 0
    index, _ = load_index(user_id)
    return index.ntotal if index else 0
