# Setup & Installation

## Prerequisites

- Python 3.11+
- Node.js 20+
- ~2 GB free disk space for the FashionCLIP model weights (downloaded on
  first use — optional, see [CV pipeline](#cv-pipeline-cpu-only-by-default))

## 1. Clone & enter the project

```bash
git clone <your-repo-url> vestia
cd vestia
```

## 2. Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env                # adjust if needed — defaults work for local dev
```

Initialize the database (creates `data/db/vestia.db`, runs migrations,
seeds the 9 occasion types):

```bash
alembic upgrade head
```

Optionally seed 30 sample wardrobe items + 7 days of outfit history for a
populated demo:

```bash
python -m app.database.seed
```

Start the API:

```bash
uvicorn app.main:app --reload --port 8000
```

Verify: `curl http://localhost:8000/health` → `{"status":"ok",...}`.
Interactive docs at `http://localhost:8000/docs`.

## 3. Frontend setup

```bash
cd ../frontend
npm install
cp .env.local.example .env.local    # defaults point to localhost:8000 via rewrites
npm run dev
```

Open `http://localhost:3000` — it redirects to `/dashboard`.

## CV Pipeline (CPU-only by default)

On first image upload, `app/cv/fashion_clip.py` lazily downloads
**FashionCLIP** (`patrickjohncyh/fashion-clip`, ~600 MB) via
`transformers`. This requires `torch` and `transformers`
(`requirements.txt` includes both). No GPU is required — inference runs on
CPU, just slower (a few seconds per image).

**If `torch`/`transformers` aren't installed**, `pipeline.py`
automatically falls back to `_stub.py`, which returns randomized-but-valid
metadata so the rest of the app (rules engine, planner, frontend) works
end-to-end for development without the ML dependencies. Every upload via
the stub is flagged `needs_review: true`.

## FAISS (optional)

`faiss-cpu` (in `requirements.txt`) enables `/wardrobe/{id}/similar` and
`/wardrobe/clusters`. If not installed, these endpoints return `[]` / `{}`
and the rest of the app is unaffected.

## Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

174 tests across `tests/unit/`, `tests/integration/`, and `tests/api/` —
see [DEVELOPMENT.md](./DEVELOPMENT.md#testing) for details.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `RuntimeError: Directory 'data/uploads' does not exist` on startup | Run from `backend/` so relative paths resolve, or run `mkdir -p data/{db,uploads,faiss_index}` first |
| `pip install` fails on `opencv-python-headless` | Ensure `libgl1`/`libglib2.0-0` are installed (see `backend/Dockerfile`) |
| Frontend shows no images | Confirm backend is running on port 8000 — Next.js rewrites proxy `/uploads/*` there |
| `faiss-cpu not installed` warning | Harmless — similarity/clustering features degrade to empty results |
