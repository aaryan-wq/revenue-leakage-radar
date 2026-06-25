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
# Edit .env with your Clerk keys
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

### 4. Frontend

```bash
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Sprint 1 Exit Criteria

- [x] App runs locally
- [x] PostgreSQL schema migrated
- [x] Clerk authentication configured
- [x] Anonymous audit session created on upload
- [x] CSV upload accepted (drag-and-drop + file picker)

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
