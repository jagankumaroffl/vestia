# Vestia

**Vestia** is a personal AI wardrobe assistant that helps you organize your wardrobe and generate outfit recommendations based on your clothes, occasion, season, style, and wardrobe history.

Upload a photo of a garment and Vestia automatically analyzes its **category, color, pattern, style, season, and gender**. You can then browse your wardrobe, generate outfits, and create a full weekly outfit plan.

The recommendation engine uses a **deterministic, rule-based scoring system** rather than an LLM, making recommendations predictable and explainable.

---

## Features

* 👕 **AI Clothing Analysis** — Automatically identify garment attributes from uploaded images.
* 🎨 **Color Detection** — Extract dominant and secondary colors using computer vision.
* 🗂️ **Wardrobe Management** — Browse, filter, search, edit, and delete clothing items.
* 👔 **Outfit Generator** — Generate outfit combinations based on occasion and season.
* 📅 **Weekly Planner** — Generate Monday–Sunday outfit plans while avoiding consecutive-day repetition.
* 📊 **Dashboard** — View wardrobe statistics and today's outfit recommendation.
* 🔍 **Vector Search** — Use FAISS for similarity-based wardrobe features.
* 🧠 **Explainable Recommendations** — Outfit scores are based on color, style, occasion, season, and repetition rules.

---

## Tech Stack

| Layer                 | Technology                                       |
| --------------------- | ------------------------------------------------ |
| Frontend              | Next.js 14 · TypeScript · Tailwind CSS · Zustand |
| Backend               | FastAPI · SQLAlchemy · Pydantic v2               |
| Computer Vision       | FashionCLIP · OpenCV                             |
| Vector Search         | FAISS                                            |
| Database              | MySQL · Alembic                                  |
| Recommendation Engine | Python rule-based scoring                        |
| API Documentation     | FastAPI / Swagger                                |

---

## Project Structure

```text
vestia/
├── backend/
│   ├── app/
│   │   ├── database/
│   │   ├── models/
│   │   ├── repositories/
│   │   ├── routers/
│   │   ├── services/
│   │   ├── faiss/
│   │   └── main.py
│   ├── alembic/
│   ├── tests/
│   ├── .env.example
│   ├── requirements.txt
│   └── alembic.ini
│
├── frontend/
│   ├── app/
│   ├── components/
│   ├── stores/
│   ├── public/
│   ├── .env.local.example
│   └── package.json
│
├── docs/
│   ├── ARCHITECTURE.md
│   ├── DATA_FLOW.md
│   ├── DATABASE_SCHEMA.md
│   ├── API.md
│   ├── SETUP.md
│   ├── DEVELOPMENT.md
│   └── DEPLOYMENT.md
│
├── docker-compose.yml
└── README.md
```

---

# Getting Started

Vestia can be run using either **Docker** or a **manual local development setup**.

## Prerequisites

### Docker Setup

Install:

* Docker
* Docker Compose

### Manual Setup

Install:

* Python **3.11+**
* Node.js **20+**
* MySQL

---

# Option 1 — Docker

Docker is the easiest way to run the complete application.

### 1. Clone or extract the project

Open a terminal in the project directory:

```bash
cd vestia
```

### 2. Build and start the application

```bash
docker compose up --build
```

Wait for the backend and frontend services to start.

The frontend waits for the backend health check before starting.

### 3. Open Vestia

**Frontend**

```text
http://localhost:3000
```

**Backend API**

```text
http://localhost:8000
```

**Interactive API documentation**

```text
http://localhost:8000/docs
```

**Backend health check**

```text
http://localhost:8000/health
```

### 4. Seed sample wardrobe data

To populate the application with sample wardrobe data:

```bash
docker compose exec backend python -m app.database.seed
```

This creates sample wardrobe data containing approximately 30 items and 7 days of wardrobe history.

### 5. Stop the application

```bash
docker compose down
```

### Remove all Docker data

⚠️ This removes the database, uploaded images, and FAISS data.

```bash
docker compose down -v
```

---

# Option 2 — Manual Local Setup

Manual setup is recommended when developing or modifying Vestia.

## Backend Setup

### 1. Open the backend directory

```bash
cd vestia/backend
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

### 3. Activate the virtual environment

**Windows PowerShell**

```powershell
.venv\Scripts\Activate.ps1
```

**Windows Command Prompt**

```cmd
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

You should see `(.venv)` at the beginning of your terminal prompt.

### 4. Install Python dependencies

```bash
pip install -r requirements.txt
```

If your environment reports an `externally managed environment` error, use:

```bash
pip install -r requirements.txt --break-system-packages
```

> On Windows with a normal virtual environment, the `--break-system-packages` option is generally not required.

---

## MySQL Database Setup

Vestia requires a MySQL database named `vestia`.

### 1. Create the database

Open MySQL and run:

```sql
CREATE DATABASE vestia;
```

### 2. Create the Vestia MySQL user

Run:

```sql
CREATE USER 'vestia'@'localhost' IDENTIFIED BY 'password';
```

### 3. Grant database permissions

```sql
GRANT ALL PRIVILEGES ON vestia.* TO 'vestia'@'localhost';
```

### 4. Apply the permissions

```sql
FLUSH PRIVILEGES;
```

### 5. Verify the user

```sql
SELECT user, host
FROM mysql.user
WHERE user = 'vestia';
```

You should see:

```text
+--------+-----------+
| user   | host      |
+--------+-----------+
| vestia | localhost |
+--------+-----------+
```

---

## Configure Environment Variables

Copy the example environment file.

**Windows PowerShell**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS**

```bash
cp .env.example .env
```

Update `.env` if your MySQL configuration differs from the default configuration.

---

## Create Database Tables

Run the Alembic migrations:

```bash
alembic upgrade head
```

This creates the required Vestia database tables.

---

## Create the Initial User

Before uploading clothing images, create a user in the `users` table.

Open MySQL and run:

```sql
USE vestia;

INSERT INTO users (
    username,
    email,
    body_type,
    gender,
    preferred_style
)
VALUES (
    'testuser',
    'testuser@vestia.com',
    'average',
    'male',
    'casual'
);
```

Verify the user:

```sql
SELECT * FROM users;
```

The user should have:

```text
id = 1
```

This is required because clothing items reference the user through `user_id`.

---

## Optional — Seed Sample Data

To populate the application with sample wardrobe data:

```bash
python -m app.database.seed
```

---

## Start the Backend

Run:

```bash
uvicorn app.main:app --reload --port 8000
```

The backend will be available at:

```text
http://localhost:8000
```

### Verify the backend

Open:

```text
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "service": "Vestia",
  "version": "1.0.0"
}
```

### API Documentation

Open:

```text
http://localhost:8000/docs
```

This provides the interactive Swagger API documentation.

---

# Frontend Setup

Keep the backend running and open a **second terminal**.

### 1. Navigate to the frontend

```bash
cd vestia/frontend
```

### 2. Install dependencies

```bash
npm install
```

### 3. Configure the frontend environment

**Windows PowerShell**

```powershell
Copy-Item .env.local.example .env.local
```

**Linux / macOS**

```bash
cp .env.local.example .env.local
```

The default configuration points the frontend to the backend running on port `8000`.

### 4. Start the development server

```bash
npm run dev
```

### 5. Open Vestia

```text
http://localhost:3000
```

The application will redirect to the Dashboard.

---

# Using the Application

## Dashboard

Provides an overview of your wardrobe, including:

* Wardrobe statistics
* Category breakdowns
* Color breakdowns
* Style breakdowns
* Season information
* Today's outfit recommendation

## Wardrobe

Browse and manage your clothing collection.

You can:

* Search clothing items
* Filter by attributes
* View clothing images
* Edit clothing metadata
* Delete clothing items

## Upload

Upload a photo containing **one garment**.

Vestia analyzes the image and attempts to identify:

* Category
* Subcategory
* Primary color
* Secondary color
* Pattern
* Style
* Season
* Gender

The detected information can be reviewed and edited before saving.

## Outfit Generator

Select an occasion and season to generate outfit recommendations from your existing wardrobe.

Recommendations are scored using:

1. Color compatibility
2. Style compatibility
3. Occasion suitability
4. Season suitability
5. Repetition / wardrobe history

## Weekly Planner

Generate a complete Monday–Sunday outfit plan.

The planner attempts to maximize variety while preventing consecutive-day repetition of tops and bottoms.

---

# AI & Computer Vision

Vestia uses computer vision for automatic clothing analysis.

### FashionCLIP

The first image upload may trigger an automatic download of the FashionCLIP model.

The model is approximately **600 MB** and requires internet access during the initial download.

No GPU is required. The model runs on the CPU, although processing can take several seconds per image.

### OpenCV

OpenCV is used to analyze clothing images and extract dominant colors using computer-vision techniques.

### Fallback Mode

If the required ML dependencies are unavailable or the FashionCLIP model cannot be downloaded, Vestia can fall back to a built-in **stub mode**.

In stub mode:

* Uploads can still be tested.
* Valid clothing metadata is generated.
* Generated metadata may not represent the actual garment.
* Items can be manually reviewed and corrected.

---

# Running Tests

From the backend directory:

```bash
cd vestia/backend
```

Run the test suite:

```bash
python -m pytest tests/ -v
```

The test suite covers the recommendation engine, database repositories, and API endpoints.

---

# Troubleshooting

## `RuntimeError: Directory 'data/uploads' does not exist`

Make sure the backend is running from the `backend` directory.

If necessary, create the required directories manually.

**Linux / macOS:**

```bash
mkdir -p data/db data/uploads data/faiss_index
```

**Windows PowerShell:**

```powershell
New-Item -ItemType Directory -Force data\db
New-Item -ItemType Directory -Force data\uploads
New-Item -ItemType Directory -Force data\faiss_index
```

---

## `Access denied for user 'vestia'@'localhost'`

Make sure the MySQL user exists:

```sql
SELECT user, host
FROM mysql.user
WHERE user = 'vestia';
```

If the user does not exist:

```sql
CREATE USER 'vestia'@'localhost' IDENTIFIED BY 'password';

GRANT ALL PRIVILEGES ON vestia.* TO 'vestia'@'localhost';

FLUSH PRIVILEGES;
```

---

## Foreign key error involving `clothing_items`

If you see an error similar to:

```text
FOREIGN KEY constraint fails
```

make sure a user exists before uploading clothing items:

```sql
SELECT * FROM users;
```

If the table is empty, create the initial user:

```sql
INSERT INTO users (
    username,
    email,
    body_type,
    gender,
    preferred_style
)
VALUES (
    'testuser',
    'testuser@vestia.com',
    'average',
    'male',
    'casual'
);
```

---

## Frontend loads but clothing images are not displayed

Make sure the backend is running:

```text
http://localhost:8000/health
```

The frontend retrieves clothing images through the backend.

---

## `faiss-cpu not installed`

This warning does not necessarily prevent the application from starting.

FAISS-dependent similarity and clustering functionality may return empty results when FAISS is unavailable.

---

## OpenCV / NumPy `_ARRAY_API` error

If you see an error similar to:

```text
AttributeError: _ARRAY_API not found
```

check the installed package versions:

```bash
pip show numpy
pip show opencv-python
pip show opencv-python-headless
pip show faiss-cpu
```

This can occur when compiled packages are incompatible with the installed NumPy version.

Do not change package versions randomly. Check the project's `requirements.txt` and installed dependency versions before making changes.

---

# Resetting the Database

## Docker

Stop the containers and remove their persistent data:

```bash
docker compose down -v
```

Then rebuild:

```bash
docker compose up --build
```

---

## Manual Setup

Run the appropriate database reset procedure for your configured MySQL environment, then recreate the schema with:

```bash
alembic upgrade head
```

After the tables are created, recreate the initial user:

```sql
INSERT INTO users (
    username,
    email,
    body_type,
    gender,
    preferred_style
)
VALUES (
    'testuser',
    'testuser@vestia.com',
    'average',
    'male',
    'casual'
);
```

---

# Documentation

Additional technical documentation is available in the `docs/` directory.

| Document                                     | Description                                        |
| -------------------------------------------- | -------------------------------------------------- |
| [Architecture](./docs/ARCHITECTURE.md)       | System architecture and component responsibilities |
| [Data Flow](./docs/DATA_FLOW.md)             | Image upload pipeline and weekly planning logic    |
| [Database Schema](./docs/DATABASE_SCHEMA.md) | Database tables and relationships                  |
| [API Reference](./docs/API.md)               | API endpoints and request/response examples        |
| [Setup Guide](./docs/SETUP.md)               | Detailed installation and setup instructions       |
| [Development Guide](./docs/DEVELOPMENT.md)   | Development workflow, migrations, and testing      |
| [Deployment Guide](./docs/DEPLOYMENT.md)     | Docker and deployment information                  |

---

# API

Once the backend is running, interactive API documentation is available at:

```text
http://localhost:8000/docs
```

FastAPI also provides an alternative ReDoc interface:

```text
http://localhost:8000/redoc
```

---

# License

This project is intended for educational and development purposes.
