# Docker Deployment

## Quick Start

From the project root:

```bash
docker compose up --build
```

- Backend: `http://localhost:8000` (docs at `/docs`)
- Frontend: `http://localhost:3000`

Data persists across rebuilds in three named volumes:
`vestia-db`, `vestia-uploads`, `vestia-faiss`.

## What `docker-compose.yml` Does

```mermaid
flowchart LR
    subgraph Host
        P1["localhost:3000"]
        P2["localhost:8000"]
    end

    subgraph Docker Network
        FE["frontend container<br/>Next.js (standalone)"]
        BE["backend container<br/>uvicorn"]
        V1[("vestia-db")]
        V2[("vestia-uploads")]
        V3[("vestia-faiss")]
    end

    P1 --> FE
    P2 --> BE
    FE -- "BACKEND_INTERNAL_URL=http://backend:8000<br/>(rewrites in next.config.mjs)" --> BE
    BE --> V1
    BE --> V2
    BE --> V3
```

The frontend's `next.config.mjs` reads `BACKEND_INTERNAL_URL` to rewrite
`/api/*` and `/uploads/*` — set to `http://backend:8000` (the Docker
service name) in compose, vs. `http://localhost:8000` for local dev. No
code changes needed between environments.

`backend`'s healthcheck (`GET /health`) gates the frontend's startup via
`depends_on: condition: service_healthy`, so the frontend doesn't serve
before the API + DB are ready.

## First-Time Initialization

The backend's `lifespan` handler runs `init_db()` on startup, which creates
all tables and seeds the 9 occasion types automatically — no manual
migration step needed for a fresh container.

To seed sample wardrobe data inside the running container:

```bash
docker compose exec backend python -m app.database.seed
```

## Building Images Individually

```bash
docker build -t vestia-backend ./backend
docker build -t vestia-frontend ./frontend \
  --build-arg BACKEND_INTERNAL_URL=http://your-backend-host:8000
```

The backend image installs `libgl1`/`libglib2.0-0` for OpenCV and runs as
`uvicorn app.main:app --host 0.0.0.0 --port 8000`. The frontend image is a
3-stage build (deps → build → runner) producing a minimal `node:20-alpine`
runtime.

## Environment Variables

| Variable | Service | Default | Purpose |
|---|---|---|---|
| `DATABASE_URL` | backend | `sqlite:///./data/db/vestia.db` | Swap to PostgreSQL DSN for production |
| `ALLOWED_ORIGINS` | backend | `["http://localhost:3000"]` | CORS — add your deployed frontend origin |
| `UPLOAD_DIR` / `FAISS_INDEX_DIR` | backend | `data/uploads` / `data/faiss_index` | Mounted as named volumes |
| `BACKEND_INTERNAL_URL` | frontend | `http://localhost:8000` | Server-side rewrite target |
| `NEXT_PUBLIC_API_BASE_URL` | frontend | `/api/v1` | Browser-facing API path (rewritten by Next.js) |
| `NEXT_PUBLIC_UPLOADS_BASE_URL` | frontend | `/uploads` | Browser-facing image path |

## Migrating to PostgreSQL

1. Add a `postgres` service to `docker-compose.yml` (image
   `postgres:16-alpine`, with its own named volume).
2. Set `backend`'s `DATABASE_URL` to
   `postgresql://vestia:password@postgres:5432/vestia`.
3. Uncomment `psycopg2-binary` in `backend/requirements.txt`.
4. The existing Alembic migration (`alembic/versions/*_initial_schema.py`)
   applies unchanged via `render_as_batch=True` — run
   `docker compose exec backend alembic upgrade head` once on first boot,
   or add it to the container's entrypoint.

No application code changes are required — `app/database/connection.py`
already branches on `DATABASE_URL` scheme for pool configuration (SQLite
`StaticPool` + WAL pragmas vs. Postgres `QueuePool` with
`pool_pre_ping`/`pool_recycle`).

## Logs & Debugging

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose exec backend bash      # shell into backend container
```

Set `DEBUG=true` in the backend environment to enable SQLAlchemy query
logging (`echo=True`).
