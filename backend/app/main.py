from __future__ import annotations
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database.connection import init_db
from app.routers import upload, wardrobe, outfits, recommendations, planner, statistics

# Ensure runtime directories exist before StaticFiles mounts below —
# StaticFiles raises at import time if the directory is missing.
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
os.makedirs(settings.FAISS_INDEX_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ───────────────────────────────────────────────────────────────
    init_db()
    yield
    # ── Shutdown ──────────────────────────────────────────────────────────────
    # connection pool is cleaned up by SQLAlchemy automatically


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-powered personal wardrobe assistant.",
    version=settings.APP_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    #allow_origins=settings.ALLOWED_ORIGINS,
    allow_origins=[
        "http://localhost:3001",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files (uploaded clothing images) ───────────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# ── Routers ───────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(upload.router,          prefix=PREFIX, tags=["Upload"])
app.include_router(wardrobe.router,        prefix=PREFIX, tags=["Wardrobe"])
app.include_router(outfits.router,         prefix=PREFIX, tags=["Outfits"])
app.include_router(recommendations.router, prefix=PREFIX, tags=["Recommendations"])
app.include_router(planner.router,         prefix=PREFIX, tags=["Planner"])
app.include_router(statistics.router,      prefix=PREFIX, tags=["Statistics"])


@app.get("/health", tags=["System"])
def health_check():
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}
