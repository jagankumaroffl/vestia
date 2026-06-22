"""
FAISS similarity search operations.

Provides:
  - find_similar_items    : kNN search by embedding vector
  - find_duplicates       : items likely to be the same garment
  - cluster_wardrobe      : group wardrobe into style clusters (K-Means on FAISS index)
"""
from __future__ import annotations

import json
import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

from app.faiss.index_manager import load_index, _FAISS_AVAILABLE

logger = logging.getLogger(__name__)

# Distance thresholds (L2 on L2-normalised 512-dim vectors)
# L2 distance on unit vectors ∈ [0, 2]. Cosine similarity = 1 - d²/2
DUPLICATE_THRESHOLD = 0.15    # very similar — likely same item
SIMILAR_THRESHOLD   = 0.60    # same style / category family


# ── Core search ───────────────────────────────────────────────────────────────

def find_similar_items(
    user_id: int,
    query_embedding: List[float],
    k: int = 5,
    exclude_item_id: Optional[int] = None,
) -> List[Dict]:
    """
    kNN search in the user's FAISS index.

    Returns list of dicts: [{"item_id": int, "distance": float, "similarity": float}]
    sorted nearest-first.
    """
    if not _FAISS_AVAILABLE:
        return []

    index, item_ids = load_index(user_id)
    if index is None or index.ntotal == 0:
        return []

    # Request k+1 to allow excluding the query item itself
    k_request = min(k + 1, index.ntotal)
    query_vec = np.array([query_embedding], dtype=np.float32)
    distances, positions = index.search(query_vec, k_request)

    results = []
    for dist, pos in zip(distances[0], positions[0]):
        if pos < 0 or pos >= len(item_ids):
            continue
        found_id = item_ids[pos]
        if found_id == exclude_item_id:
            continue
        # Convert L2 distance to cosine similarity (valid for unit vectors)
        similarity = max(0.0, 1.0 - float(dist) / 2.0)
        results.append({
            "item_id":    found_id,
            "distance":   round(float(dist), 4),
            "similarity": round(similarity, 4),
        })
        if len(results) >= k:
            break

    return results


def find_duplicates(
    user_id: int,
    query_embedding: List[float],
    exclude_item_id: Optional[int] = None,
) -> List[Dict]:
    """
    Return items within DUPLICATE_THRESHOLD — likely the same garment
    uploaded twice. Used during upload to warn the user.
    """
    candidates = find_similar_items(
        user_id, query_embedding, k=5, exclude_item_id=exclude_item_id
    )
    return [c for c in candidates if c["distance"] <= DUPLICATE_THRESHOLD]


def find_outfit_complements(
    user_id: int,
    anchor_embedding: List[float],
    target_category: str,
    all_items_embeddings: Dict[int, List[float]],
    k: int = 3,
) -> List[int]:
    """
    Find clothing items from `target_category` whose embeddings are
    most complementary (moderate distance — not too similar, not too far).

    Used by the outfit engine to suggest diverse but compatible pairings.
    """
    if not all_items_embeddings:
        return []

    anchor_vec = np.array(anchor_embedding, dtype=np.float32)
    scored: List[Tuple[int, float]] = []

    for item_id, emb in all_items_embeddings.items():
        item_vec = np.array(emb, dtype=np.float32)
        dist = float(np.linalg.norm(anchor_vec - item_vec))
        # Ideal complement: moderate distance (0.3–0.8)
        complement_score = 1.0 - abs(dist - 0.55) / 0.55
        scored.append((item_id, complement_score))

    scored.sort(key=lambda x: x[1], reverse=True)
    return [iid for iid, _ in scored[:k]]


def cluster_wardrobe(
    user_id: int,
    n_clusters: int = 4,
) -> Dict[int, List[int]]:
    """
    K-Means clustering of wardrobe embeddings.
    Returns {cluster_id: [item_id, ...]} for wardrobe organisation.
    Requires faiss-cpu; returns {} if unavailable or index empty.
    """
    if not _FAISS_AVAILABLE:
        return {}

    try:
        import faiss as _faiss
        from app.faiss.index_manager import _new_index
    except ImportError:
        return {}

    index, item_ids = load_index(user_id)
    if index is None or index.ntotal < n_clusters:
        return {}

    vecs = index.reconstruct_n(0, index.ntotal).astype(np.float32)
    n_clusters = min(n_clusters, len(item_ids))

    kmeans = _faiss.Kmeans(vecs.shape[1], n_clusters, niter=20, verbose=False)
    kmeans.train(vecs)
    _, assignments = kmeans.index.search(vecs, 1)

    clusters: Dict[int, List[int]] = {i: [] for i in range(n_clusters)}
    for pos, (cluster_arr,) in enumerate(assignments):
        cluster_id = int(cluster_arr)
        if pos < len(item_ids):
            clusters[cluster_id].append(item_ids[pos])

    return clusters


def embedding_from_json(embedding_json: str) -> Optional[List[float]]:
    """Parse a JSON-serialised embedding string from DB. Returns None on error."""
    if not embedding_json:
        return None
    try:
        return json.loads(embedding_json)
    except (json.JSONDecodeError, TypeError):
        return None
