# Database Schema

9 tables, normalized, SQLite for development with a PostgreSQL-portable
schema (see `backend/app/database/schema.sql` for raw DDL and
`backend/alembic/` for migrations).

## Entity-Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ CLOTHING_ITEMS : owns
    USERS ||--o{ OUTFITS : owns
    USERS ||--|| USER_PREFERENCES : has
    USERS ||--o{ OUTFIT_HISTORY : has
    USERS ||--|| WARDROBE_STATISTICS : has
    USERS ||--o{ OUTFIT_RECOMMENDATIONS : has

    OUTFITS ||--o{ OUTFIT_ITEMS : contains
    CLOTHING_ITEMS ||--o{ OUTFIT_ITEMS : "used in"
    OUTFITS ||--o{ OUTFIT_RECOMMENDATIONS : "recommended as"
    OUTFITS ||--o{ OUTFIT_HISTORY : "worn as"

    USERS {
        int id PK
        string username
        string email
        string body_type
        string gender
        string preferred_style
    }

    CLOTHING_ITEMS {
        int id PK
        int user_id FK
        string image_path
        string category
        string subcategory
        string primary_color
        string secondary_color
        string pattern
        string style
        string season
        string gender
        text embedding "JSON float[512]"
        json tags
        bool is_active
        int wear_count
        datetime last_worn
    }

    OUTFITS {
        int id PK
        int user_id FK
        string name
        string occasion
        string season
        float total_score
        float color_score
        float style_score
        float occasion_score
        float season_score
        float repetition_score
    }

    OUTFIT_ITEMS {
        int id PK
        int outfit_id FK
        int clothing_item_id FK
        string position "top|bottom|shoes|outerwear|accessory"
    }

    OUTFIT_RECOMMENDATIONS {
        int id PK
        int user_id FK
        int outfit_id FK
        string occasion
        string season
        float score
        datetime recommended_date
        bool is_accepted
    }

    OCCASION_TYPES {
        int id PK
        string name UK
        json required_categories
        json optional_categories
        string description
    }

    USER_PREFERENCES {
        int id PK
        int user_id FK "UK"
        json preferred_occasions
        json preferred_styles
        json preferred_colors
        json avoid_colors
    }

    OUTFIT_HISTORY {
        int id PK
        int user_id FK
        int outfit_id FK
        datetime worn_date
        string occasion
        text notes
    }

    WARDROBE_STATISTICS {
        int id PK
        int user_id FK "UK"
        int total_items
        json category_breakdown
        json color_breakdown
        json most_worn_items
        json least_worn_items
    }
```

## Table Notes

**`clothing_items`** is the core table. `embedding` stores a 512-dim
FashionCLIP vector as a JSON string — the FAISS index is the source of
truth for similarity search, but this column lets the index be rebuilt from
the database alone (`faiss/index_manager.rebuild_index()`). `is_active`
implements soft-delete; deleted items are excluded from wardrobe listings
and statistics but remain in `outfit_items`/`outfit_history` for historical
integrity.

**`outfits`** stores the five sub-scores alongside `total_score` so the
frontend can render the score breakdown (`ScoreDisplay` component) without
recomputation. Every outfit returned by `/generate-outfit` or
`/weekly-plan` is persisted here, even before the user marks it worn.

**`outfit_items`** is the many-to-many junction between outfits and
clothing items, tagged with `position` (`top` / `bottom` / `shoes` /
`outerwear` / `accessory`) — this is how `OutfitCard` and `DayOutfit` know
which slot each item fills.

**`outfit_history`** is written only when the user explicitly marks an
outfit as worn (`POST /outfits/{id}/worn`). `repetition_rules.py` queries
this table (last 2 days) to penalize repeated topwear/bottomwear.

**`occasion_types`** is a seeded lookup table mirroring
`app/rules/occasion_rules.OCCASION_RULES` — kept in the database for
potential future admin editing, though the rules engine currently reads
from the Python constants for performance.

**`wardrobe_statistics`** is a cache table refreshed by
`StatsRepository.compute_and_upsert()`; `GET /statistics` can also compute
fresh aggregates on demand via `StatisticsService`.

## Indexes

```sql
CREATE INDEX idx_clothing_user_id  ON clothing_items(user_id);
CREATE INDEX idx_clothing_category ON clothing_items(category);
CREATE INDEX idx_clothing_style    ON clothing_items(style);
CREATE INDEX idx_clothing_season   ON clothing_items(season);
CREATE INDEX idx_outfits_user_id   ON outfits(user_id);
CREATE INDEX idx_outfits_occasion  ON outfits(occasion);
CREATE INDEX idx_outfit_items_outfit ON outfit_items(outfit_id);
CREATE INDEX idx_history_user_worn   ON outfit_history(user_id, worn_date);
```

## PostgreSQL Migration

The schema uses no SQLite-specific types. To migrate:

1. Set `DATABASE_URL=postgresql://user:pass@host:5432/vestia` in `.env`.
2. Install the Postgres driver: `pip install psycopg2-binary`.
3. Run `alembic upgrade head` — `env.py` reads `DATABASE_URL` from settings
   and `render_as_batch=True` is harmless on Postgres (only needed for
   SQLite's `ALTER TABLE` limitations).
4. `AUTOINCREMENT` → Postgres `SERIAL`/`IDENTITY` is handled automatically
   by SQLAlchemy's dialect-aware DDL compiler.
