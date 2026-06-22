"""
Database seeder for development and demo environments.

Run:
    cd backend
    python -m app.database.seed

Seeds:
  - Default user
  - 30 clothing items (varied category / colour / style / season)
  - Occasion types (idempotent via init_db)
"""
from __future__ import annotations
import random
from datetime import datetime, timedelta, timezone

from app.database.connection import init_db, SessionLocal
from app.database.models import (
    User, ClothingItem, Outfit, OutfitItem, OutfitHistory, UserPreference,
)

# ── Sample data pools ─────────────────────────────────────────────────────────

TOPS = [
    ("topwear", "t-shirt",       "white",      None,         "solid",   "casual",         "summer"),
    ("topwear", "t-shirt",       "black",      None,         "solid",   "casual",         "all_season"),
    ("topwear", "t-shirt",       "grey",       None,         "graphic", "casual",         "all_season"),
    ("topwear", "polo",          "navy blue",  None,         "solid",   "smart_casual",   "summer"),
    ("topwear", "polo",          "white",      None,         "solid",   "smart_casual",   "all_season"),
    ("topwear", "oxford shirt",  "light blue", None,         "solid",   "business_casual","all_season"),
    ("topwear", "oxford shirt",  "white",      None,         "solid",   "formal",         "all_season"),
    ("topwear", "casual shirt",  "olive green",None,         "solid",   "casual",         "summer"),
    ("topwear", "casual shirt",  "burgundy",   None,         "solid",   "smart_casual",   "winter"),
    ("topwear", "hoodie",        "grey",       None,         "solid",   "casual",         "winter"),
    ("topwear", "sweater",       "navy blue",  None,         "solid",   "smart_casual",   "winter"),
    ("topwear", "formal shirt",  "white",      "light blue", "striped", "formal",         "all_season"),
]

BOTTOMS = [
    ("bottomwear", "jeans",              "navy blue", None,    "solid", "casual",         "all_season"),
    ("bottomwear", "jeans",              "black",     None,    "solid", "smart_casual",   "all_season"),
    ("bottomwear", "chinos",             "beige",     None,    "solid", "smart_casual",   "summer"),
    ("bottomwear", "chinos",             "olive green",None,   "solid", "casual",         "all_season"),
    ("bottomwear", "formal trousers",    "black",     None,    "solid", "formal",         "all_season"),
    ("bottomwear", "formal trousers",    "navy blue", None,    "solid", "business_casual","all_season"),
    ("bottomwear", "shorts",             "beige",     None,    "solid", "casual",         "summer"),
    ("bottomwear", "slim fit trousers",  "grey",      None,    "solid", "business_casual","all_season"),
]

FOOTWEAR = [
    ("footwear", "sneakers",      "white",  None,  "solid", "casual",         "all_season"),
    ("footwear", "sneakers",      "black",  None,  "solid", "casual",         "all_season"),
    ("footwear", "formal shoes",  "black",  None,  "solid", "formal",         "all_season"),
    ("footwear", "formal shoes",  "brown",  None,  "solid", "business_casual","all_season"),
    ("footwear", "loafers",       "brown",  None,  "solid", "smart_casual",   "all_season"),
    ("footwear", "boots",         "brown",  None,  "solid", "casual",         "winter"),
]

OUTERWEAR = [
    ("outerwear", "blazer",         "navy blue", None, "solid", "business_casual","all_season"),
    ("outerwear", "blazer",         "black",     None, "solid", "formal",         "all_season"),
    ("outerwear", "denim jacket",   "light blue",None, "solid", "casual",         "all_season"),
    ("outerwear", "leather jacket", "black",     None, "solid", "smart_casual",   "winter"),
]

ALL_ITEMS = TOPS + BOTTOMS + FOOTWEAR + OUTERWEAR

CATEGORY_TO_POSITION = {
    "topwear":   "top",
    "bottomwear":"bottom",
    "footwear":  "shoes",
    "outerwear": "outerwear",
    "accessory": "accessory",
}


def seed(clear: bool = False) -> None:
    init_db()
    db = SessionLocal()

    try:
        if clear:
            _clear_data(db)

        # ── User ─────────────────────────────────────────────────────────────
        user = db.query(User).filter_by(id=1).first()
        if not user:
            user = User(id=1, username="default", email="user@vestia.app",
                        body_type="regular", gender="unisex")
            db.add(user)
            db.commit()
            db.refresh(user)
            prefs = UserPreference(user_id=user.id,
                                   preferred_styles=["casual","smart_casual"],
                                   preferred_occasions=["casual","office"])
            db.add(prefs)
            db.commit()

        # ── Clothing items ────────────────────────────────────────────────────
        existing = db.query(ClothingItem).filter_by(user_id=1).count()
        if existing == 0:
            for i, row in enumerate(ALL_ITEMS):
                cat, subcat, primary, secondary, pattern, style, season = row
                item = ClothingItem(
                    user_id=1,
                    image_path=f"1/seed_{i:03d}_{subcat.replace(' ','_')}.jpg",
                    category=cat,
                    subcategory=subcat,
                    primary_color=primary,
                    secondary_color=secondary,
                    pattern=pattern,
                    style=style,
                    season=season,
                    gender="unisex",
                    wear_count=random.randint(0, 12),
                )
                db.add(item)
            db.commit()

        # ── Sample outfit history ─────────────────────────────────────────────
        history_count = db.query(OutfitHistory).filter_by(user_id=1).count()
        if history_count == 0:
            items = db.query(ClothingItem).filter_by(user_id=1).all()
            tops    = [i for i in items if i.category == "topwear"]
            bottoms = [i for i in items if i.category == "bottomwear"]
            shoes   = [i for i in items if i.category == "footwear"]

            for days_ago in range(1, 8):
                if not tops or not bottoms or not shoes:
                    break
                outfit = Outfit(
                    user_id=1,
                    occasion="casual",
                    season="all_season",
                    total_score=round(random.uniform(0.6, 0.9), 2),
                    color_score=round(random.uniform(0.5, 1.0), 2),
                    style_score=round(random.uniform(0.5, 1.0), 2),
                    occasion_score=round(random.uniform(0.5, 1.0), 2),
                    season_score=1.0,
                    repetition_score=1.0,
                )
                db.add(outfit)
                db.flush()

                for item in [random.choice(tops), random.choice(bottoms), random.choice(shoes)]:
                    db.add(OutfitItem(
                        outfit_id=outfit.id,
                        clothing_item_id=item.id,
                        position=CATEGORY_TO_POSITION[item.category],
                    ))

                worn_dt = datetime.now(timezone.utc) - timedelta(days=days_ago)
                db.add(OutfitHistory(
                    user_id=1, outfit_id=outfit.id,
                    worn_date=worn_dt, occasion="casual",
                ))

            db.commit()

        items_total  = db.query(ClothingItem).filter_by(user_id=1).count()
        outfits_total = db.query(Outfit).filter_by(user_id=1).count()
        history_total = db.query(OutfitHistory).filter_by(user_id=1).count()

        print(f"Seed complete — items={items_total}, outfits={outfits_total}, history={history_total}")

    finally:
        db.close()


def _clear_data(db) -> None:
    from app.database.models import OutfitHistory, OutfitItem, Outfit, ClothingItem
    db.query(OutfitHistory).delete()
    db.query(OutfitItem).delete()
    db.query(Outfit).delete()
    db.query(ClothingItem).delete()
    db.commit()
    print("Cleared existing seed data.")


if __name__ == "__main__":
    import sys
    clear = "--clear" in sys.argv
    seed(clear=clear)
