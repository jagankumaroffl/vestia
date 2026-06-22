# Vestia

A personal AI wardrobe assistant. Upload photos of your clothes, and Vestia
identifies category, color, pattern, style, and season automatically — then
generates outfit recommendations and full weekly plans using a
deterministic, rule-based scoring engine (no LLM in the recommendation
path).

## Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 14 (App Router) · TypeScript · Tailwind CSS · Zustand |
| Backend | FastAPI · SQLAlchemy · Pydantic v2 |
| Computer Vision | FashionCLIP (zero-shot) · OpenCV (color extraction) |
| Vector Search | FAISS |
| Database | SQLite (dev) / PostgreSQL-portable, Alembic migrations |
| Recommendation Engine | Pure-Python rules: color, style, occasion, season, repetition |

## Quick Start

```bash
docker compose up --build
```

→ Frontend: `http://localhost:3000` · Backend docs: `http://localhost:8000/docs`

For local (non-Docker) development, see [docs/SETUP.md](./docs/SETUP.md).

## How It Works

1. **Upload** a photo of one garment. FashionCLIP classifies category,
   subcategory, style, pattern, season, and gender; OpenCV extracts the
   dominant colors via K-Means. Everything is editable before saving.
2. **Wardrobe** shows your full closet as a filterable, searchable grid.
3. **Outfit Generator** picks an occasion + season and returns the
   highest-scoring combinations from your actual wardrobe, with a
   breakdown of the five scoring factors.
4. **Weekly Planner** generates a full Monday–Sunday plan, guaranteeing no
   consecutive-day repeats of tops or bottoms while maximizing variety
   across the week.
5. **Dashboard** summarizes your wardrobe — category/color/style/season
   breakdowns, outfit stats, and today's pick.

## Documentation

- [Architecture](./docs/ARCHITECTURE.md) — system diagram, layer
  responsibilities, scoring weights
- [Data Flow](./docs/DATA_FLOW.md) — upload pipeline, weekly planning
  algorithm, scoring sequence
- [Database Schema](./docs/DATABASE_SCHEMA.md) — ER diagram, table notes,
  PostgreSQL migration
- [API Reference](./docs/API.md) — every endpoint with request/response
  examples
- [Setup & Installation](./docs/SETUP.md)
- [Local Development](./docs/DEVELOPMENT.md) — running tests, migrations,
  extending the rules engine
- [Docker Deployment](./docs/DEPLOYMENT.md)

## Testing

```bash
cd backend && python -m pytest tests/ -v
```

174 tests: 138 unit/integration (rules engine, repositories) + 36 API
contract tests.

## Project Status

All 8 development phases complete:

- [x] Phase 1 — Architecture & folder structure
- [x] Phase 2 — Backend foundation (config, models, schema, repositories, services, routers)
- [x] Phase 3 — CV pipeline (FashionCLIP + OpenCV + FAISS)
- [x] Phase 4 — Database layer (Alembic, seeding, WAL tuning, repo tests)
- [x] Phase 5 — Recommendation engine (color/style/occasion/season/repetition rules)
- [x] Phase 6 — Frontend (5 pages, Zustand stores, "Digital Atelier" design system)
- [x] Phase 7 — Testing (174 tests across unit/integration/API)
- [x] Phase 8 — Deployment & documentation (this README + `docs/`)
