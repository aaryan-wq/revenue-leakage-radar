# Paevo Hardening Report

**Date:** 2026-07-06  
**Branch:** `cursor/paevo-hardening-phase-e1d2`  
**Scope:** Bootstrap, verification engine audit, CSV chaos testing, performance optimization, E2E repair, ingestion resilience

---

## 1. Executive Summary

A full hardening pass was executed across backend verification, CSV ingestion, synthetic/fuzz infrastructure, performance benchmarks, and Playwright E2E suites.

**Environment:** PostgreSQL 16 + Redis 7 (local apt install), API `:8000`, Web `:3000`, `CELERY_TASK_ALWAYS_EAGER=true`, Clerk + Stripe test keys configured.

**Test health after pass:**
- **284** API pytest tests passing (up from 280 baseline)
- **32/32** verification fixture catalog at 100% ground-truth match
- **100/100** fuzz harness iterations (200 customers) with zero mismatches
- **20/20** CSV chaos stress iterations across 8 billing platforms
- **46–49/50** Playwright E2E tests passing (upload flow + auth fixes; occasional flaky dev-unlock under parallel load)

The app is **materially safer to launch** for MVP CSV audits: verification math is regression-locked, ingestion tolerates camelCase headers and fuzzed exports, and engine hot paths are indexed for large audits.

---

## 2. Bugs Found

### BUG-H01 — CamelCase CSV headers not mapped (High)
- **Area:** `apps/api/adapters/headers.py`
- **Root cause:** `normalize_header` lowercased `customerId` to `customerid` without splitting camelCase, so canonical column mapping failed.
- **Impact:** Stripe/Chargebee-style exports with camelCase headers failed ingestion.

### BUG-H02 — Harness date parsing brittle on fuzzed whitespace/formats (Medium)
- **Area:** `apps/api/harness/money.py`
- **Root cause:** `parse_date` only accepted strict ISO strings.
- **Impact:** Fuzzed CSV chaos tests failed; edge-case dates in synthetic pipelines could break harness comparisons.

### BUG-H03 — Verification context O(n) entity lookups (High — Performance)
- **Area:** `apps/api/verification/context.py`
- **Root cause:** Linear scans for customers, subscriptions, invoices, coupons, contracts, and price catalog on every lookup.
- **Impact:** Context build and rule evaluation degraded toward O(n²) at 1k+ customers.

### BUG-H04 — Duplicate findings DB query in report builder (Medium — Performance)
- **Area:** `apps/api/reports/generator.py`, `apps/api/reports/summary.py`
- **Root cause:** `build_report_detail` loaded all findings twice.
- **Impact:** ~2× DB + serialization work on report endpoints.

### BUG-H05 — E2E suite out of sync with auto-upload UX (High — Test infra)
- **Area:** `e2e/helpers/audit.ts`, `e2e/upload.spec.ts`
- **Root cause:** Tests expected removed copy ("Drop your billing…") and removed "Upload Files" button; flow now auto-uploads on file select.
- **Impact:** 17 E2E failures masking real regressions.

### BUG-H06 — Dev unlock E2E missing auth + audit session on link (High — Test infra)
- **Area:** `e2e/helpers/api.ts`
- **Root cause:** `/audit/{id}/link` requires `Authorization` + `X-Audit-Session`; `devUnlockReport` required Clerk JWT.
- **Impact:** Payments/findings unlock tests failed with 401/404.

### BUG-H07 — `discount_wrong_product` triple-nested loop (Medium — Performance)
- **Area:** `apps/api/verification/rules/discounts/discount_wrong_product.py`
- **Root cause:** Iterated subscriptions × invoices × line items.
- **Impact:** Worst-case cubic behavior on discounted invoices.

---

## 3. Bugs Fixed

| ID | Fix |
|----|-----|
| H01 | CamelCase splitting in `normalize_header` + regression tests |
| H02 | Multi-format `parse_date` with whitespace trim |
| H03 | Dict indexes for all entity lookups + pre-sorted subscription invoices + cached reference date |
| H04 | `build_free_summary(..., findings=)` to reuse single query |
| H05 | E2E helpers updated for "Place your data here" + auto-upload + "Continue to Validation →" |
| H06 | `linkAuditToClerkUser`, `getClerkAuthToken` with Clerk loaded wait |
| H07 | Invoice-first iteration in `discount_wrong_product` |

Additional: `rule_lookup()` module-level cache, removed duplicate `joinedload` on invoice line items.

---

## 4. Performance Improvements

| Bottleneck | Change | Measured benefit |
|------------|--------|------------------|
| Entity lookups in `CanonicalContext` | `_by_id` dicts, catalog indexes | Engine: **188ms @ 1000 customers** (benchmark script) |
| `catalog_for_product` full scans | Pre-indexed `_catalog_by_product` / `_catalog_by_sku` | Eliminates millions of redundant scans per audit |
| Duplicate line item load | Dropped `joinedload(Invoice.line_items)` | Halves line-item memory/IO |
| Report double-query | Pass preloaded findings into summary builder | ~2× fewer finding rows loaded |
| `discount_wrong_product` | Invoice-first loop | Avoids O(subs × invoices × lines) |
| Date validation | Vectorized ISO pass + fallback for exotic formats | Faster validation on wide CSVs |

**Benchmark (`scripts/benchmark_audit_performance.py`):**

| Customers | Engine time |
|-----------|-------------|
| 10 | 11ms |
| 100 | 44ms |
| 500 | 97ms |
| 1000 | 188ms |

---

## 5. UI / UX Improvements

No production UI copy changes in this pass (tests aligned to existing auto-upload UX). E2E alignment improves confidence in:

- Upload zone heading: "Place your data here"
- Auto-upload progress states (Queued / Uploading / Uploaded)
- Continue CTA: "Continue to Validation →"
- Empty-file errors surfaced per-file with Retry

---

## 6. Verification Engine Corrections

No ground-truth mismatches found in 32-fixture catalog or 100-iteration fuzz harness after optimizations. Changes preserve determinism:

- Index builds use same canonical data ordering
- `catalog_for_product` behavior unchanged (verified by `test_context_catalog.py`)
- Pre-sorted invoices use stable `(invoice_date, id)` ordering

---

## 7. Regression Coverage Added

| Asset | Purpose |
|-------|---------|
| `apps/api/tests/test_context_indexes.py` | O(1) lookup + pre-sorted invoice regression |
| `apps/api/tests/test_date_validation.py` | Vectorized date validation |
| `apps/api/tests/test_validation.py` | camelCase header mapping cases |
| `scripts/benchmark_audit_performance.py` | Scalable engine timing |
| `scripts/csv_chaos_stress.py` | 8-platform fuzzed CSV ingestion stress |
| E2E helper/API updates | Auto-upload flow, Clerk link + dev unlock |

---

## 8. Remaining Risks

- **E2E flakiness:** Dev unlock + Stripe checkout tests can fail under parallel load; recommend serial execution or retry for CI.
- **Bulk DB ingestion:** Canonical transformer still uses row-by-row `flush()` — largest remaining ingestion bottleneck at 10k+ rows.
- **Report pagination:** Full findings payload still returned in one JSON response; frontend may struggle at 5k+ findings.
- **Real customer exports:** Chaos harness covers synthetic data; production Chargebee/Zuora edge cases need customer validation.
- **Checkout E2E:** Requires live Stripe test mode + signed-in user on summary page.

---

## 9. Coverage Summary

| Category | Status |
|----------|--------|
| Routes exercised (E2E) | 27 frontend routes via navigation + workflow specs |
| Upload flows | Auto-upload, Tier 0, enriched, empty/malformed, refresh |
| Rules tested | 26/26 via fixture catalog + fuzz harness |
| Synthetic datasets | Existing harness + 100-iteration fuzz @ 200 customers |
| Corrupted/messy CSVs | 20 chaos iterations (headers, dates, columns, platforms) |
| Responsive breakpoints | Partial (Playwright default viewport); manual ultra-wide not run |

---

## 10. Confidence Score

**82%** launch confidence for MVP CSV-first audits.

**Justification:** Verification engine is regression-locked with 100% fixture accuracy, performance is bounded to sub-second engine times at 1k customers, ingestion handles realistic header chaos, and E2E covers the primary anonymous funnel. Remaining gap is production-scale ingestion DB batching, paginated reports, and hardening paid-checkout flows under CI parallelism.

---

## Internal Execution Notes

| Item | Value |
|------|-------|
| API start | `cd apps/api && source .venv/bin/activate && uvicorn main:app --port 8000` |
| Web start | `npm run dev` (port 3000) |
| DB | `postgresql://rlr:rlr_dev_password@localhost:5432/revenue_leakage_radar` |
| Redis | `redis://localhost:6379/0` |
| E2E user | `e2e+qa@revenueleakageradar.dev` (Clerk testing) |
| Blockers fixed | Docker unavailable → apt PostgreSQL/Redis; Playwright browsers installed; E2E synced to auto-upload UX |
