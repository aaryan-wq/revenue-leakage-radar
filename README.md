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

#### Clerk authentication (recommended)

Install the Clerk CLI and link this repo to your Clerk application.

**Important:** This is an npm workspaces monorepo. The Next.js app is in `apps/web`, so run
`clerk init` from that directory (not the repo root):

```bash
npm install -g clerk
clerk auth login
cd apps/web
clerk init --app app_3FdbXDyolZYLnuPxsuNVlpAtgX2
clerk doctor
cd ../..
```

Or from the repo root:

```bash
npm run clerk:init
```

`clerk init` writes keys to `apps/web/.env.local`. The web app also loads the shared root `.env`.
Restart the dev server after init. Sign In / Sign Up appear in the top nav when keys are present.

Clerk application: `app_3FdbXDyolZYLnuPxsuNVlpAtgX2`

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

**Important:** Run the worker from `apps/api` using the project virtualenv, not from the repo root and not with global Python.

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

1. Upload Tier 0 files (`invoice_line_items.csv` + `prices.csv` or `price_catalog.csv`) at `/upload`
2. Validation auto-starts when Tier 0 is complete
3. Optionally add Tier 1 files (subscriptions, invoices, customers) for broader rule coverage
4. Review platform detection, column mapping, and validation results at `/validation`
5. Data is normalized into the canonical PostgreSQL schema on success

## Sprint 3 Flow

1. Complete Sprint 2 validation at `/validation`
2. Click **Start Scan** to begin deterministic verification at `/analysis`
3. Engine runs 20 leakage rules against canonical data (Celery or eager mode)
4. Findings and recoverable ARR are persisted; scan completion summary is shown

## Sprint 4 Flow

1. After scan completes, view the free Revenue Verification Summary at `/summary`
2. Signed-in users can access purchased reports at `/report/{id}`
3. Dashboard at `/dashboard` shows audit history for authenticated users
4. Export PDF and CSV from purchased reports

## Sprint 5 Flow (Payments)

### Stripe setup (test mode)

1. Create a [Stripe test account](https://dashboard.stripe.com/test/apikeys)
2. Create two Products in Stripe Dashboard:
   - **Detailed Report**, one-time Price → copy `price_...` to `STRIPE_PRICE_SINGLE_REPORT`
   - **Annual Membership**, recurring yearly Price → copy to `STRIPE_PRICE_ANNUAL_MEMBERSHIP`
3. Add keys to `.env`:

```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...   # from stripe listen (below)
STRIPE_PRICE_SINGLE_REPORT=price_...
STRIPE_PRICE_ANNUAL_MEMBERSHIP=price_...
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
NEXT_PUBLIC_WEB_URL=http://localhost:3000
```

4. Forward webhooks locally:

```bash
stripe listen --forward-to localhost:8000/webhooks/stripe
```

### Manual E2E checklist (MVP complete)

1. `docker compose up -d`, PostgreSQL and Redis
2. Run API, Celery worker (or `CELERY_TASK_ALWAYS_EAGER=true`), and `npm run dev`
3. `alembic upgrade head` in `apps/api`
4. **Anonymous path:** `/upload` with Tier 0 CSVs from `apps/api/tests/fixtures/` → validation → analysis → `/summary`
5. Confirm **Data Coverage** section, verification checklist, and toast notifications
6. **Enriched path:** Re-run with subscriptions + invoices + customers → more rules execute
7. Sign in → **Unlock Report** → Stripe test card `4242 4242 4242 4242`
8. Webhook fires → `/checkout/success` → full report unlocks at `/report/{id}`
9. Export **PDF**, **Findings CSV**, and **Evidence CSV** from report page
10. Open a finding at `/findings/{id}` → verify evidence → **Copy Link**
11. **Dashboard:** company name, report credits, Open/Delete audit, PDF + CSV download
12. **Annual membership:** purchase → use **Use 1 Credit** on a second audit summary
13. Cancel checkout → `/checkout/cancel` → report stays locked
14. **Security:** after ingestion, confirm raw CSVs are removed from `apps/api/uploads/{audit_id}/`
15. Review `/account`, `/privacy`, and `/terms` pages
16. `cd apps/api && pytest`, all tests pass

## API Endpoints (Sprint 2–5)

| Method | Path | Description |
|--------|------|-------------|
| POST | `/audit/{id}/validate` | Start ingestion pipeline |
| GET | `/audit/{id}/validation` | Full validation report |
| POST | `/audit/{id}/scan` | Start verification scan |
| GET | `/audit/{id}/scan` | Scan status and results |
| GET | `/summary/{audit_id}` | Free revenue summary (includes coverage) |
| GET | `/findings/{id}` | Finding detail (purchased report) |
| GET | `/exports/csv/{report_id}` | Findings CSV export |
| GET | `/exports/evidence/{report_id}` | Evidence CSV export |
| GET | `/exports/pdf/{report_id}` | PDF export |
| DELETE | `/audit/{audit_id}` | Delete audit (authenticated owner) |
| GET | `/dashboard` | Authenticated audit history |
| POST | `/checkout` | Create Stripe Checkout session |
| POST | `/webhooks/stripe` | Stripe webhook handler |
| GET | `/billing` | Plan and purchase history |
| POST | `/reports/{id}/unlock-credit` | Unlock report using membership credit |

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

## Production Deploy

### Service topology

| Service | Platform | Root / notes |
|---------|----------|----------------|
| Frontend | Vercel | `apps/web` (see `apps/web/vercel.json`) |
| API | Railway | `apps/api` — [`start.sh`](apps/api/start.sh) runs uvicorn |
| Celery worker | Railway | `apps/api` + [`railway.worker.toml`](apps/api/railway.worker.toml) |
| Postgres | Railway | Plugin |
| Redis | Railway | Plugin (required for Celery) |
| Object storage | Cloudflare R2 | Uploads + report exports |

### Railway: separate config files for API and worker

Both services use root directory `apps/api`, but **different config-as-code files**:

| Service | Config file path (Railway → Settings) | Start process |
|---------|----------------------------------------|---------------|
| API | `/apps/api/railway.toml` | [`start.sh`](apps/api/start.sh) → uvicorn, `/health` check, `alembic upgrade head` on deploy |
| Worker | `/apps/api/railway.worker.toml` | [`Dockerfile`](apps/api/Dockerfile) → Celery, **no health check**, no migrations |

**Worker service setup:**
1. Root directory: `apps/api`
2. **Config file path:** `/apps/api/railway.worker.toml` (absolute from repo root; does not follow root directory)
3. Copy the **same env vars** as the API (`DATABASE_URL`, `REDIS_URL`, all `R2_*`, etc.)
4. Do not set a custom start command in the UI — Dockerfile `CMD` runs Celery

**API service setup:**
1. Root directory: `apps/api`
2. Config file path: `/apps/api/railway.toml` (default if unset)

After deploy, worker logs should show `celery@... ready.` and `Task ... run_ingestion received` when you validate an upload.

### Domains

- `paevo.co` → Vercel (frontend)
- `api.paevo.co` → Railway (API)
- Stripe webhook → `https://api.paevo.co/webhooks/stripe`

### Railway environment (API + worker)

```
ENVIRONMENT=production
CELERY_TASK_ALWAYS_EAGER=false
CELERY_WORKER_CONCURRENCY=2
DATABASE_URL=<railway postgres>
REDIS_URL=<railway redis>
WEB_URL=https://paevo.co
CORS_ORIGINS=https://paevo.co,https://www.paevo.co
ALLOWED_HOSTS=api.paevo.co
STORAGE_BACKEND=r2
R2_ACCOUNT_ID=...
R2_ACCESS_KEY_ID=...
R2_SECRET_ACCESS_KEY=...
R2_ENDPOINT=https://<accountid>.r2.cloudflarestorage.com
R2_BUCKET_UPLOADS=paevo-prod-uploads
R2_BUCKET_REPORTS=paevo-prod-reports
CLERK_SECRET_KEY=...
CLERK_JWT_ISSUER=...
CLERK_JWT_AUDIENCE=https://paevo.co
STRIPE_SECRET_KEY=...
STRIPE_WEBHOOK_SECRET=...
STRIPE_PRICE_SINGLE_REPORT=...
POSTHOG_API_KEY=...
SENTRY_DSN=...
RESEND_API_KEY=...
FROM_EMAIL=hello@paevo.co
SUPPORT_EMAIL=aaryan@paevo.co
```

Migrations run automatically via `apps/api/railway.toml` pre-deploy (`alembic upgrade head`).

### Vercel environment

```
NEXT_PUBLIC_APP_URL=https://paevo.co
NEXT_PUBLIC_API_URL=https://api.paevo.co
NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY=pk_live_...
CLERK_SECRET_KEY=sk_live_...
NEXT_PUBLIC_POSTHOG_KEY=...
NEXT_PUBLIC_POSTHOG_HOST=https://us.i.posthog.com
NEXT_PUBLIC_SENTRY_DSN=...
NEXT_PUBLIC_SUPPORT_EMAIL=aaryan@paevo.co
```

### Post-deploy smoke test

1. `GET https://api.paevo.co/health` — database and redis healthy
2. Anonymous upload → validation → scan (R2 + Celery + Redis)
3. Free summary at `/summary/{audit_id}`
4. Sign in → Stripe checkout → webhook unlocks report
5. Export PDF/CSV (cached in R2 on repeat download)
6. Confirm purchase confirmation email via Resend
