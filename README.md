# Revenue Leakage Radar

Detect recoverable recurring revenue from billing CSV exports using deterministic verification rules.

## Prerequisites

- Node.js 20+
- npm 10+ (or pnpm 9+)
- Python 3.12+
- Docker & Docker Compose (for PostgreSQL and Redis)

## Quick Start

### 1. Start infrastructure

```bash
docker compose up -d
```

### 2. Configure environment

```bash
cp .env.example .env
# Optional: set OPENAI_API_KEY for AI column mapping (fallback works without it)
# For local dev without Celery worker: CELERY_TASK_ALWAYS_EAGER=true
```

### 3. Backend

```bash
cd apps/api
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
alembic upgrade head
uvicorn main:app --reload --port 8000
```

### 4. Celery worker (Sprint 2+)

**Important:** Run the worker from `apps/api` using the project virtualenv — not from the repo root and not with global Python.

In a separate terminal:

```powershell
cd apps/api
.venv\Scripts\activate
celery -A workers.celery_app worker -l info --pool=solo
```

Or use the helper script (Windows):

```powershell
cd apps/api
.\run-worker.ps1
```

macOS / Linux:

```bash
cd apps/api
chmod +x run-worker.sh
./run-worker.sh
```

**Without a worker:** set `CELERY_TASK_ALWAYS_EAGER=true` in `.env` to run ingestion inline in the API process.

### 5. Frontend

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Sprint 2 Flow

1. Upload all 5 required billing CSVs at `/upload`
2. Validation auto-starts when the last file is uploaded
3. Review platform detection, column mapping, and validation results at `/validation`
4. Data is normalized into the canonical PostgreSQL schema on success

## Sprint 3 Flow

1. Complete Sprint 2 validation at `/validation`
2. Click **Start Scan** to begin deterministic verification at `/analysis`
3. Engine runs 20 leakage rules against canonical data (Celery or eager mode)
4. Findings and recoverable ARR are persisted; scan completion summary is shown

## API Endpoints (Sprint 2–3)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/audit/{id}/validate` | Start ingestion pipeline |
| GET | `/audit/{id}/validation` | Full validation report |
| POST | `/audit/{id}/scan` | Start verification scan |
| GET | `/audit/{id}/scan` | Scan status and results |

## Tests

```bash
cd apps/api
pytest
```

## Project Structure

```
apps/
  web/          Next.js 15 frontend
  api/          FastAPI backend
packages/
  shared/       Shared TypeScript types
  ui/           Shared UI components
  config/       Shared configs
docs/           Product, technical, and design specs
```

## Documentation

- [Product Spec](docs/product-spec.md)
- [Technical Spec](docs/technical-spec.md)
- [Design System](docs/design-system.md)
- [Build Plan](docs/build-plan.md)
