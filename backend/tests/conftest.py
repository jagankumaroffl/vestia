"""
Shared pytest fixtures.
Each test gets a fresh in-memory SQLite database — fast and fully isolated.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database.connection import Base
import app.database.models  # noqa: F401


@pytest.fixture(scope="function")
def db():
    """
    Yields a SQLAlchemy session backed by an in-memory SQLite database.
    Tables are created fresh for every test function and dropped afterwards.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def seed_user(db):
    """Create a default User row and return it."""
    from app.database.models import User
    user = User(id=1, username="testuser", email="test@vestia.app")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def seed_clothing(db, seed_user):
    """Seed one item per key category and return them as a dict."""
    from app.database.models import ClothingItem
    items = {}
    specs = [
        ("top",     "topwear",    "t-shirt",          "white",     "solid",  "casual",         "all_season"),
        ("bottom",  "bottomwear", "jeans",             "navy blue", "solid",  "casual",         "all_season"),
        ("shoes",   "footwear",   "sneakers",          "white",     "solid",  "casual",         "all_season"),
        ("blazer",  "outerwear",  "blazer",            "navy blue", "solid",  "business_casual","all_season"),
        ("formal_top",  "topwear",    "oxford shirt",  "light blue","solid",  "formal",         "all_season"),
        ("formal_bot",  "bottomwear", "formal trousers","black",    "solid",  "formal",         "all_season"),
        ("formal_shoe", "footwear",   "formal shoes",  "black",     "solid",  "formal",         "all_season"),
    ]
    for key, cat, subcat, color, pattern, style, season in specs:
        item = ClothingItem(
            user_id=seed_user.id,
            image_path=f"1/{key}.jpg",
            category=cat, subcategory=subcat,
            primary_color=color, pattern=pattern,
            style=style, season=season, gender="unisex",
        )
        db.add(item)
    db.commit()
    all_items = db.query(ClothingItem).filter_by(user_id=seed_user.id).all()
    for item in all_items:
        items[item.subcategory] = item
    return items
