"""
Shared fixtures for API contract tests.

Each test gets:
  - A fresh in-memory SQLite DB (via dependency override of get_db)
  - Isolated temp directories for uploads + FAISS index (via monkeypatched settings)
  - A FastAPI TestClient wired to the above
"""
import io
import pytest
from PIL import Image
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database.connection import Base, get_db
import app.database.models  # noqa: F401


@pytest.fixture()
def client(tmp_path, monkeypatch):
    # ── Isolated filesystem paths for uploads / FAISS index ───────────────────
    upload_dir = tmp_path / "uploads"
    faiss_dir = tmp_path / "faiss_index"
    upload_dir.mkdir()
    faiss_dir.mkdir()

    from app.config import settings
    monkeypatch.setattr(settings, "UPLOAD_DIR", str(upload_dir))
    monkeypatch.setattr(settings, "FAISS_INDEX_DIR", str(faiss_dir))

    # ── Isolated in-memory DB ──────────────────────────────────────────────────
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # Seed default user (id=1) + occasion types — app normally does this
    # via init_db() in lifespan, which we bypass with TestClient.
    from app.database.models import User, OccasionType
    seed_db = TestingSessionLocal()
    seed_db.add(User(id=1, username="default", email="user@vestia.app"))
    seed_db.add_all([
        OccasionType(name="casual",           required_categories=["topwear","bottomwear","footwear"],             optional_categories=["accessory"]),
        OccasionType(name="college",          required_categories=["topwear","bottomwear","footwear"],             optional_categories=["accessory"]),
        OccasionType(name="office",           required_categories=["topwear","bottomwear","footwear"],             optional_categories=["outerwear","accessory"]),
        OccasionType(name="business_meeting", required_categories=["topwear","bottomwear","footwear"],             optional_categories=["outerwear","accessory"]),
        OccasionType(name="formal_event",     required_categories=["topwear","bottomwear","footwear","outerwear"], optional_categories=["accessory"]),
        OccasionType(name="party",            required_categories=["topwear","bottomwear","footwear"],             optional_categories=["accessory"]),
        OccasionType(name="date_night",       required_categories=["topwear","bottomwear","footwear"],             optional_categories=["accessory"]),
        OccasionType(name="wedding",          required_categories=["topwear","bottomwear","footwear","outerwear"], optional_categories=["accessory"]),
        OccasionType(name="travel",           required_categories=["topwear","bottomwear","footwear"],             optional_categories=["outerwear","accessory"]),
    ])
    seed_db.commit()
    seed_db.close()

    from app.main import app
    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture()
def sample_image_bytes() -> bytes:
    """A small solid-color JPEG, valid for upload tests."""
    img = Image.new("RGB", (100, 100), (0, 0, 128))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def upload_item(client: TestClient, image_bytes: bytes, **form_overrides) -> dict:
    """Helper: upload one clothing image with optional field overrides, return JSON body."""
    files = {"file": ("item.jpg", image_bytes, "image/jpeg")}
    data = {k: v for k, v in form_overrides.items() if v is not None}
    resp = client.post("/api/v1/upload", files=files, data=data)
    assert resp.status_code == 201, resp.text
    return resp.json()
