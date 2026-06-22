-- ============================================================
--  Vestia — Database Schema
--  Primary target: SQLite (dev) / PostgreSQL (prod)
--  All AUTOINCREMENT → SERIAL in PostgreSQL
-- ============================================================

CREATE TABLE IF NOT EXISTS users (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    username        TEXT    NOT NULL UNIQUE,
    email           TEXT    NOT NULL UNIQUE,
    body_type       TEXT    NOT NULL DEFAULT 'regular',   -- slim | athletic | regular | plus
    gender          TEXT    NOT NULL DEFAULT 'unisex',
    preferred_style TEXT,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME
);

-- ── Clothing Items ───────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clothing_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    image_path      TEXT    NOT NULL,

    -- CV-extracted fields
    category        TEXT    NOT NULL,   -- topwear | bottomwear | footwear | accessory | outerwear
    subcategory     TEXT    NOT NULL,   -- t-shirt | jeans | oxford shirt | …
    primary_color   TEXT    NOT NULL,
    secondary_color TEXT,
    pattern         TEXT    NOT NULL DEFAULT 'solid',   -- solid | striped | checked | printed | floral | graphic
    style           TEXT    NOT NULL,   -- casual | formal | business_casual | smart_casual | party
    season          TEXT    NOT NULL DEFAULT 'all_season',  -- summer | winter | rainy | all_season
    gender          TEXT    NOT NULL DEFAULT 'unisex',

    -- FashionCLIP embedding (JSON serialized float array)
    embedding       TEXT,

    -- User-defined tags (JSON array)
    tags            TEXT    NOT NULL DEFAULT '[]',

    -- Lifecycle
    is_active       INTEGER NOT NULL DEFAULT 1,
    wear_count      INTEGER NOT NULL DEFAULT 0,
    last_worn       DATETIME,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME
);

CREATE INDEX IF NOT EXISTS idx_clothing_user_id    ON clothing_items(user_id);
CREATE INDEX IF NOT EXISTS idx_clothing_category   ON clothing_items(category);
CREATE INDEX IF NOT EXISTS idx_clothing_style      ON clothing_items(style);
CREATE INDEX IF NOT EXISTS idx_clothing_season     ON clothing_items(season);

-- ── Outfits ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS outfits (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name             TEXT,
    occasion         TEXT    NOT NULL,
    season           TEXT    NOT NULL,

    -- Scores from rules engine
    total_score      REAL    NOT NULL DEFAULT 0.0,
    color_score      REAL    NOT NULL DEFAULT 0.0,
    style_score      REAL    NOT NULL DEFAULT 0.0,
    occasion_score   REAL    NOT NULL DEFAULT 0.0,
    season_score     REAL    NOT NULL DEFAULT 0.0,
    repetition_score REAL    NOT NULL DEFAULT 0.0,

    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_outfits_user_id  ON outfits(user_id);
CREATE INDEX IF NOT EXISTS idx_outfits_occasion ON outfits(occasion);

-- ── Outfit Items (junction) ───────────────────────────────────
CREATE TABLE IF NOT EXISTS outfit_items (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    outfit_id       INTEGER NOT NULL REFERENCES outfits(id) ON DELETE CASCADE,
    clothing_item_id INTEGER NOT NULL REFERENCES clothing_items(id) ON DELETE CASCADE,
    position        TEXT    NOT NULL    -- top | bottom | shoes | outerwear | accessory
);

CREATE INDEX IF NOT EXISTS idx_outfit_items_outfit ON outfit_items(outfit_id);

-- ── Outfit Recommendations ────────────────────────────────────
CREATE TABLE IF NOT EXISTS outfit_recommendations (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id          INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    outfit_id        INTEGER NOT NULL REFERENCES outfits(id) ON DELETE CASCADE,
    occasion         TEXT    NOT NULL,
    season           TEXT    NOT NULL,
    score            REAL    NOT NULL DEFAULT 0.0,
    recommended_date DATETIME,
    is_accepted      INTEGER NOT NULL DEFAULT 0,
    created_at       DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Occasion Types ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS occasion_types (
    id                   INTEGER PRIMARY KEY AUTOINCREMENT,
    name                 TEXT    NOT NULL UNIQUE,
    required_categories  TEXT    NOT NULL DEFAULT '[]',   -- JSON
    optional_categories  TEXT    NOT NULL DEFAULT '[]',   -- JSON
    description          TEXT
);

-- Seed occasions
INSERT OR IGNORE INTO occasion_types (name, required_categories, optional_categories, description) VALUES
  ('casual',          '["topwear","bottomwear","footwear"]',               '["accessory"]',              'Everyday relaxed wear'),
  ('college',         '["topwear","bottomwear","footwear"]',               '["accessory"]',              'Campus / college wear'),
  ('office',          '["topwear","bottomwear","footwear"]',               '["outerwear","accessory"]',  'Standard office environment'),
  ('business_meeting','["topwear","bottomwear","footwear"]',               '["outerwear","accessory"]',  'Client-facing meetings'),
  ('formal_event',    '["topwear","bottomwear","footwear","outerwear"]',   '["accessory"]',              'Formal ceremonies'),
  ('party',           '["topwear","bottomwear","footwear"]',               '["accessory"]',              'Social parties'),
  ('date_night',      '["topwear","bottomwear","footwear"]',               '["accessory"]',              'Romantic evenings'),
  ('wedding',         '["topwear","bottomwear","footwear","outerwear"]',   '["accessory"]',              'Wedding guest attire'),
  ('travel',          '["topwear","bottomwear","footwear"]',               '["outerwear","accessory"]',  'Travel / transit');

-- ── User Preferences ─────────────────────────────────────────
CREATE TABLE IF NOT EXISTS user_preferences (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id             INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    preferred_occasions TEXT    NOT NULL DEFAULT '[]',   -- JSON
    preferred_styles    TEXT    NOT NULL DEFAULT '[]',   -- JSON
    preferred_colors    TEXT    NOT NULL DEFAULT '[]',   -- JSON
    avoid_colors        TEXT    NOT NULL DEFAULT '[]',   -- JSON
    updated_at          DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ── Outfit History ────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS outfit_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id    INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    outfit_id  INTEGER NOT NULL REFERENCES outfits(id) ON DELETE CASCADE,
    worn_date  DATETIME NOT NULL,
    occasion   TEXT,
    notes      TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_history_user_worn ON outfit_history(user_id, worn_date);

-- ── Wardrobe Statistics ───────────────────────────────────────
CREATE TABLE IF NOT EXISTS wardrobe_statistics (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id           INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    total_items       INTEGER NOT NULL DEFAULT 0,
    category_breakdown TEXT   NOT NULL DEFAULT '{}',   -- JSON
    color_breakdown    TEXT   NOT NULL DEFAULT '{}',   -- JSON
    most_worn_items    TEXT   NOT NULL DEFAULT '[]',   -- JSON
    least_worn_items   TEXT   NOT NULL DEFAULT '[]',   -- JSON
    updated_at         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
