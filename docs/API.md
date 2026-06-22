# API Reference

Base URL: `http://localhost:8000/api/v1` (interactive docs at
`http://localhost:8000/docs`)

All endpoints operate in single-user mode by default
(`user_id=1`, configurable via `DEFAULT_USER_ID`); most accept an optional
`user_id` query parameter for multi-user setups.

---

## Health

### `GET /health`

```json
{ "status": "ok", "service": "Vestia", "version": "1.0.0" }
```

---

## Upload

### `POST /api/v1/upload`

`multipart/form-data`. Runs the CV pipeline, saves the image, indexes the
embedding in FAISS, and persists a `clothing_items` row.

| Field | Type | Required | Notes |
|---|---|---|---|
| `file` | file | yes | JPEG/PNG/WebP, ≤10 MB |
| `category` | string | no | Override CV detection |
| `subcategory` | string | no | Override CV detection |
| `style` | string | no | Override CV detection |
| `season` | string | no | Override CV detection |
| `tags` | string | no | Comma-separated |
| `user_id` | int | no | Default `1` |

**Response `201`**

```json
{
  "clothing_item_id": 14,
  "image_path": "1/9f3e2c1a.jpg",
  "category": "topwear",
  "subcategory": "oxford shirt",
  "primary_color": "light blue",
  "secondary_color": "white",
  "pattern": "solid",
  "style": "business_casual",
  "season": "all_season",
  "gender": "unisex",
  "confidence": 0.87,
  "needs_review": false
}
```

`needs_review: true` when `confidence < 0.6` — the frontend Upload page
surfaces a correction form in this case.

**Errors**: `415` unsupported MIME type, `413` file too large.

---

## Wardrobe

### `GET /api/v1/wardrobe`

Query params: `category`, `style`, `season`, `color`, `pattern`, `skip`,
`limit` (1–200, default 50), `user_id`.

```json
[
  {
    "id": 14,
    "user_id": 1,
    "image_path": "1/9f3e2c1a.jpg",
    "category": "topwear",
    "subcategory": "oxford shirt",
    "primary_color": "light blue",
    "secondary_color": "white",
    "pattern": "solid",
    "style": "business_casual",
    "season": "all_season",
    "gender": "unisex",
    "tags": [],
    "is_active": true,
    "wear_count": 3,
    "last_worn": "2026-06-10T08:00:00Z",
    "created_at": "2026-05-01T12:00:00Z"
  }
]
```

### `GET /api/v1/wardrobe/{item_id}`

Returns a single item (shape as above). `404` if not found.

### `PATCH /api/v1/wardrobe/{item_id}`

Body: any subset of `ClothingItemUpdate` fields (`category`, `subcategory`,
`primary_color`, `secondary_color`, `pattern`, `style`, `season`, `gender`,
`tags`, `is_active`). Returns the updated item. `404` if not found.

### `DELETE /api/v1/wardrobe/{item_id}`

Soft-deletes (`is_active=false`). `204 No Content`. `404` if not found.

### `GET /api/v1/wardrobe/{item_id}/similar?k=5`

FAISS kNN search on the item's embedding. Returns up to `k` similar
`ClothingItem` objects (excluding the item itself). Returns `[]` if
`faiss-cpu` isn't installed or the item has no embedding.

### `GET /api/v1/wardrobe/clusters?n_clusters=4`

K-Means clustering of the user's wardrobe embeddings.

```json
{ "0": [1, 4, 9], "1": [2, 5], "2": [3, 6, 7], "3": [8] }
```

Keys are cluster indices, values are `clothing_items.id` lists. Returns
`{}` if the wardrobe has fewer items than `n_clusters` or FAISS is
unavailable.

---

## Outfits

### `POST /api/v1/generate-outfit`

```json
{ "occasion": "office", "season": "all_season", "count": 3 }
```

`occasion` must be one of: `casual`, `college`, `office`,
`business_meeting`, `formal_event`, `party`, `date_night`, `wedding`,
`travel`. `count` is 1–10 (default 3).

**Response `201`** — array of `Outfit`:

```json
[
  {
    "id": 42,
    "user_id": 1,
    "name": null,
    "occasion": "office",
    "season": "all_season",
    "scores": {
      "total_score": 0.91,
      "color_score": 0.95,
      "style_score": 0.90,
      "occasion_score": 1.0,
      "season_score": 1.0,
      "repetition_score": 1.0
    },
    "items": [
      {
        "id": 101,
        "position": "top",
        "clothing_item": {
          "id": 14, "category": "topwear", "subcategory": "oxford shirt",
          "primary_color": "light blue", "style": "business_casual",
          "image_path": "1/9f3e2c1a.jpg"
        }
      }
    ],
    "created_at": "2026-06-13T09:00:00Z"
  }
]
```

**Errors**:
- `422` — wardrobe is missing a *required* category for this occasion
  (e.g. no `outerwear` for `formal_event`/`wedding`), or `occasion` is
  invalid.

### `GET /api/v1/outfits`

Query params: `occasion`, `season`, `skip`, `limit` (1–100, default 20),
`user_id`. Returns previously generated `Outfit` objects, sorted by
`total_score` descending.

### `GET /api/v1/outfits/{outfit_id}`

Single `Outfit`. `404` if not found.

### `POST /api/v1/outfits/{outfit_id}/worn`

```json
{ "outfit_id": 42, "worn_date": "2026-06-13T08:00:00Z", "occasion": "office", "notes": "Felt great" }
```

All fields except `outfit_id` optional (`worn_date` defaults to now).
Writes an `outfit_history` row and increments `wear_count` on every item in
the outfit. `204 No Content`.

### `DELETE /api/v1/outfits/{outfit_id}`

`204 No Content`. `404` if not found.

---

## Recommendations

### `GET /api/v1/recommendations?occasion=casual&season=summer&count=5`

Equivalent to `POST /generate-outfit` but read-only/idempotent in intent —
generates and persists up to `count` outfits, returned highest-scored
first. Same response shape as `generate-outfit`.

---

## Weekly Planner

### `POST /api/v1/weekly-plan`

```json
{
  "occasion": "casual",
  "season": "all_season",
  "day_overrides": { "Friday": "office", "Saturday": "party" },
  "start_date": "2026-06-15"
}
```

`day_overrides` and `start_date` are optional; `start_date` defaults to the
next Monday.

**Response `200`**

```json
{
  "week_start": "2026-06-15",
  "season": "all_season",
  "days": [
    {
      "day": "Monday",
      "date": "2026-06-15",
      "occasion": "casual",
      "score": 0.93,
      "outfit": { "...": "Outfit object, see above" },
      "note": null
    }
  ],
  "total_unique_tops": 5,
  "total_unique_bottoms": 5,
  "coverage": 1.0
}
```

`days` always has 7 entries (Monday–Sunday). `outfit: null` with a
non-empty `note` means the wardrobe couldn't satisfy that day's occasion
(e.g. `formal_event` override with no `outerwear` in the closet) —
`coverage` reflects the fraction of days successfully filled.

**Repetition guarantee**: consecutive days never repeat the same `top` or
`bottom` item unless the wardrobe genuinely has no alternative (see
[DATA_FLOW.md](./DATA_FLOW.md#2-weekly-plan-generation) for the 3-tier
fallback).

---

## Statistics

### `GET /api/v1/statistics`

```json
{
  "total_items": 32,
  "active_items": 30,
  "category_breakdown": { "topwear": 12, "bottomwear": 8, "footwear": 6, "outerwear": 4, "accessory": 0 },
  "color_breakdown": { "navy blue": 5, "white": 4, "black": 6 },
  "style_breakdown": { "casual": 14, "business_casual": 8, "formal": 5, "smart_casual": 3 },
  "season_breakdown": { "all_season": 22, "summer": 5, "winter": 3 },
  "most_worn": [{ "id": 14, "subcategory": "oxford shirt", "wear_count": 9 }],
  "least_worn": [{ "id": 22, "subcategory": "joggers", "wear_count": 0 }],
  "total_outfits_generated": 47,
  "total_outfits_worn": 12
}
```

`total_items` includes soft-deleted (`is_active=false`) items;
`active_items` does not.
