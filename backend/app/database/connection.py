"""
Database connection — SQLite dev + PostgreSQL prod.

Connection pool is tuned per backend:
  SQLite  : StaticPool (single file, no pool needed)
  Postgres: QueuePool   (pool_size=10, max_overflow=20)
"""
from __future__ import annotations
import os
from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

os.makedirs("data/db", exist_ok=True)

_is_sqlite = settings.DATABASE_URL.startswith("sqlite")

if _is_sqlite:
    from sqlalchemy.pool import StaticPool
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=settings.DEBUG,
    )
    # Enable WAL mode for better concurrent read performance
    @event.listens_for(engine, "connect")
    def _set_wal(dbapi_conn, _):
        dbapi_conn.execute("PRAGMA journal_mode=WAL")
        dbapi_conn.execute("PRAGMA foreign_keys=ON")
        dbapi_conn.execute("PRAGMA synchronous=NORMAL")
        dbapi_conn.execute("PRAGMA cache_size=-64000")   # 64 MB page cache
else:
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,      # drop stale connections before use
        pool_recycle=3600,       # recycle after 1 hour
        echo=settings.DEBUG,
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """FastAPI dependency — always yields a session and closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Create all tables. Called once at app startup."""
    from app.database import models          # noqa: F401 — registers ORM classes
    Base.metadata.create_all(bind=engine)
    _seed_occasions()


def _seed_occasions() -> None:
    """Idempotent seed of occasion_types lookup table."""
    from app.database.models import OccasionType
    db = SessionLocal()
    try:
        if db.query(OccasionType).count() > 0:
            return
        occasions = [
            OccasionType(name="casual",           required_categories=["topwear","bottomwear","footwear"],                optional_categories=["accessory"],              description="Everyday relaxed wear"),
            OccasionType(name="college",           required_categories=["topwear","bottomwear","footwear"],                optional_categories=["accessory"],              description="Campus wear"),
            OccasionType(name="office",            required_categories=["topwear","bottomwear","footwear"],                optional_categories=["outerwear","accessory"],   description="Standard office"),
            OccasionType(name="business_meeting",  required_categories=["topwear","bottomwear","footwear"],                optional_categories=["outerwear","accessory"],   description="Client-facing meetings"),
            OccasionType(name="formal_event",      required_categories=["topwear","bottomwear","footwear","outerwear"],    optional_categories=["accessory"],              description="Formal ceremonies"),
            OccasionType(name="party",             required_categories=["topwear","bottomwear","footwear"],                optional_categories=["accessory"],              description="Social events"),
            OccasionType(name="date_night",        required_categories=["topwear","bottomwear","footwear"],                optional_categories=["accessory"],              description="Romantic evenings"),
            OccasionType(name="wedding",           required_categories=["topwear","bottomwear","footwear","outerwear"],    optional_categories=["accessory"],              description="Wedding guest"),
            OccasionType(name="travel",            required_categories=["topwear","bottomwear","footwear"],                optional_categories=["outerwear","accessory"],   description="Travel / transit"),
        ]
        db.add_all(occasions)
        db.commit()
    finally:
        db.close()
