from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Vestia"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # Database - swap to PostgreSQL URL for prod
    DATABASE_URL: str = "sqlite:///./data/db/vestia.db"

    # Storage
    UPLOAD_DIR: str = "data/uploads"
    FAISS_INDEX_DIR: str = "data/faiss_index"

    # CORS
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000"]

    # CV pipeline
    FASHION_CLIP_MODEL: str = "patrickjohncyh/fashion-clip"
    EMBEDDING_DIMENSION: int = 512

    # Image validation
    MAX_IMAGE_SIZE_MB: int = 10
    ALLOWED_MIME_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # Default user id (single-user mode for now)
    DEFAULT_USER_ID: int = 1

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
