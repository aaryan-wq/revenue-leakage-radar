# QA Report, Revenue Leakage Radar

**Date:** 2026-06-25  
**Scope:** MCP browser QA, Playwright E2E, authentication, uploads, verification engine, payments, findings, security, reliability  
**Test suite:** 81 API tests passing · 50 Playwright E2E tests passing

---

## Summary

| Severity | Found | Fixed | Open |
|----------|-------|-------|------|
| Critical | 1 | 1 | 0 |
| High | 4 | 4 | 0 |
| Medium | 4 | 4 | 0 |
| Low | 2 | 1 | 1 |

All critical and high-severity issues identified in this pass have been fixed with automated regression tests.

---

## E2E QA Pass (2026-06-25)

### MCP Browser Verification

| Flow | Method | Result |
|------|--------|--------|
| Landing page load | Playwright MCP `browser_navigate` | Pass |
| Nav → Upload | MCP click "Run Free Scan" | Pass |
| Protected `/dashboard` redirect | MCP navigate unsigned | Pass → `/sign-in` |
| Upload page render | MCP snapshot | Pass |

### Playwright Regression Suite

| Area | Tests | Status |
|------|-------|--------|
| Global setup (Clerk user + auth state) | 3 | Pass |
| Analysis pipeline | 5 | Pass |
| Authentication lifecycle | 8 | Pass |
| Findings UI + math | 3 | Pass |
| Navigation (all public pages) | 11 | Pass |
| Payments + Stripe redirect | 4 | Pass |
| Security (IDOR, API auth) | 6 | Pass |
| Browser stress | 3 | Pass |
| CSV upload (valid/invalid/edge) | 7 | Pass |

**Command:** `PLAYWRIGHT_SKIP_WEBSERVER=1 npx playwright test --project=chromium` (with API + web already running)

---

## Issues

### BUG-002, E2E audit session cleared on every navigation (High)

**Severity:** High

**Reproduction:**
1. Run anonymous upload → validation → summary pipeline in Playwright.
2. `clearAuditSession()` used `page.addInitScript()` to remove `rlr_audit_id` / `rlr_audit_session`.
3. Navigate to `/findings/{id}` after dev unlock.
4. UI shows "Invalid audit session."

**Expected vs Actual:**
- Expected: Audit session persists until explicitly cleared.
- Actual: Session wiped on every subsequent page load.

**Root cause:** `addInitScript` runs on all navigations in the browser context, not just once at test start.

**Fix:** Changed `clearAuditSession()` to perform a one-time clear via `page.goto("/")` + `page.evaluate()`.

**Files changed:**
- `e2e/helpers/audit.ts`

**Regression test:** `e2e/findings.spec.ts` → "unlocked finding shows evidence and consistent leakage math"

---

### BUG-003, Upload helper did not handle manual validation redirect (Medium)

**Severity:** Medium

**Reproduction:**
1. Upload Tier 0 CSVs via UI when auto-redirect to `/validation` does not fire (API slow or tier detection lag).
2. "Continue to Validation" button visible but E2E helper waits indefinitely for URL change.

**Expected vs Actual:**
- Expected: Tests proceed whether redirect is automatic or manual.
- Actual: Playwright timeout on `waitForURL(/validation/)`.

**Root cause:** `uploadCsvFiles()` only waited for automatic redirect; did not click fallback CTA.

**Fix:** Added `ensureOnValidation()` helper that clicks "Continue to Validation" when present.

**Files changed:**
- `e2e/helpers/audit.ts`

**Regression test:** `e2e/analysis.spec.ts` → "shows loading states during validation"

---

### BUG-004, Playwright config did not start API server (Medium)

**Severity:** Medium

**Reproduction:**
1. Run `npm run test:e2e` with only frontend `webServer` configured.
2. Upload tests fail, files selected but never reach validation (API unreachable).

**Root cause:** `playwright.config.ts` only started Next.js dev server, not FastAPI on port 8000.

**Fix:** Added second `webServer` entry for uvicorn health check; `PLAYWRIGHT_SKIP_WEBSERVER=1` escape hatch documented.

**Files changed:**
- `playwright.config.ts`

**Regression test:** Full E2E suite health gate in `e2e/global.setup.ts`

---

### BUG-005, Clerk auth storage state not persisted for E2E (Medium)

**Severity:** Medium

**Reproduction:**
1. Run Playwright tests depending on authenticated `storageState`.
2. `__client_uat` cookie remained `0`, user not actually signed in.

**Root cause:** `global.setup.ts` saved storage state before verifying sign-in completed; ticket-based sign-in needed user provisioning first.

**Fix:**
- Added `e2e/helpers/auth.ts` with `ensureClerkTestUser()`, `signInTestUser()`, `signOutTestUser()`.
- Setup waits for `/dashboard` after sign-in before saving state.
- QA test user: `e2e+qa@revenueleakageradar.dev` (Clerk Backend API).

**Files changed:**
- `e2e/global.setup.ts`
- `e2e/helpers/auth.ts`
- `e2e/helpers/env.ts`
- `.env.example`

**Regression test:** `e2e/auth.spec.ts` → authenticated session tests

---

### BUG-006, Navigation test used stale CTA label (Low)

**Severity:** Low

**Reproduction:** Navigation spec looked for "Start Audit" / "Upload" link; nav uses "Run Free Scan".

**Fix:** Updated selector to `/run free scan/i`.

**Files changed:**
- `e2e/navigation.spec.ts`

**Regression test:** `e2e/navigation.spec.ts` → "top nav links are not dead"

---

### SEC-001, IDOR: Credit unlock on any report (Critical)

**Severity:** Critical

**Reproduction:**
1. User A uploads billing data anonymously (audit has no `clerk_user_id`).
2. User B signs in with membership credits.
3. User B calls `POST /reports/{report_id}/unlock-credit` with User A's `report_id`.
4. Report unlocks without payment or ownership.

**Root cause:** `unlock_with_credit` only blocked access when `audit.clerk_user_id` was set to a *different* user. Unlinked audits (`clerk_user_id IS NULL`) were treated as unlockable by any authenticated user.

**Fix:**
- Added `auth/audit_access.py` with `assert_audit_modification_access()`.
- Unlock route requires audit ownership **or** valid `X-Audit-Session` header.
- Links audit to user after access check, then consumes credit.
- Frontend passes stored audit session on unlock and checkout.

**Files changed:**
- `apps/api/auth/audit_access.py` (new)
- `apps/api/payments/routes.py`
- `apps/api/payments/entitlements.py`
- `apps/api/payments/service.py`
- `apps/web/lib/report-api.ts`
- `apps/web/components/summary/unlock-cta.tsx`
- `apps/web/components/summary/checkout-button.tsx`

**Tests added:**
- `apps/api/tests/test_audit_access.py` (8 tests)

---

### SEC-002, IDOR: Checkout hijacks foreign reports (High)

**Severity:** High

**Reproduction:**
1. Attacker obtains or guesses a `report_id`.
2. Attacker calls `POST /checkout` while signed in.
3. `link_audit_to_user()` attached the victim's audit to the attacker before Stripe payment.

**Root cause:** `create_checkout_session()` called `link_audit_to_user()` without verifying the caller owned the audit or held a valid session token.

**Fix:** `assert_audit_modification_access()` enforced before linking; checkout route forwards `X-Audit-Session`.

**Files changed:** Same as SEC-001.

**Tests added:** `test_create_checkout_session_rejects_foreign_report`

---

### SEC-003, Audit ownership overwrite (High)

**Severity:** High

**Reproduction:**
1. User A completes an audit (linked to `user_a`).
2. User B triggers `link_audit_to_user(audit, "user_b")` via checkout or fulfillment path.
3. Audit ownership silently reassigned to User B.

**Root cause:** `link_audit_to_user()` unconditionally overwrote `clerk_user_id`.

**Fix:** Reject overwrite when audit is already linked to another user; idempotent when same user.

**Files changed:**
- `apps/api/audit/service.py`

**Tests added:**
- `test_link_audit_to_user_rejects_overwrite`
- `test_link_audit_to_user_idempotent_for_same_user`

---

### SEC-004, Webhook fulfillment user mismatch (High)

**Severity:** High

**Reproduction:** If a Stripe session were created before access controls (or via compromised metadata), webhook fulfillment could link/unlock a report for a user who does not own the audit.

**Root cause:** `fulfill_checkout_session()` always called `link_audit_to_user()` without checking existing ownership.

**Fix:** Deny fulfillment when `audit.clerk_user_id` is set and does not match session metadata `clerk_user_id`. Only link when audit is unlinked.

**Files changed:**
- `apps/api/payments/service.py`

**Tests added:** `test_fulfill_checkout_session_denies_audit_owner_mismatch`

---

### SEC-005, Path traversal in upload filenames (Medium)

**Severity:** Medium

**Reproduction:** Upload file named `../../subscriptions.csv` or `subscriptions.csv\x00.exe`.

**Root cause:** Filename used for validation only; storage path is safe, but malicious names could confuse operators or bypass extension checks via null bytes.

**Fix:** Reject filenames containing `..`, `/`, `\`, or null bytes.

**Files changed:**
- `apps/api/upload/service.py`

**Tests added:** `apps/api/tests/test_upload_security.py` (4 tests)

---

### BUG-001, TypeScript build failure on validation page (Medium)

**Severity:** Medium

**Reproduction:** Run `npx tsc --noEmit` in `apps/web`.

**Root cause:** Inner `const session` declaration in `validation-page-client.tsx` shadowed outer `session` in the same block (TDZ error). `CheckoutRequest` type missing from `report-api.ts` imports.

**Fix:** Renamed inner variable to `refreshedSession`; imported `CheckoutRequest` from `@rlr/shared`.

**Files changed:**
- `apps/web/components/validation/validation-page-client.tsx`
- `apps/web/lib/report-api.ts`

**Tests added:** Typecheck (`tsc --noEmit`)

---

### OBS-001, Dev unlock endpoint unauthenticated (Low)

**Severity:** Low (development only)

**Reproduction:** `POST /dev/reports/{id}/unlock` with no auth in non-production environments.

**Root cause:** Intentional dev convenience endpoint gated by `settings.environment == "production"` → 404.

**Status:** Accepted for MVP dev workflow. **Must not be deployed with `environment != production` in public environments without additional auth.**

**Recommendation:** Add shared secret header or restrict to localhost before production hardening.

---

### OBS-002, Pytest asyncio deprecation warning (Low)

**Severity:** Low

**Reproduction:** Run pytest; warning about `asyncio_default_fixture_loop_scope`.

**Status:** Open, cosmetic; does not affect test results.

---

## Workflows Verified (Automated)

| Area | Tests | Status |
|------|-------|--------|
| **Playwright E2E (browser)** | **50** | **Pass** |
| Audit access / IDOR | 9 | Pass |
| Payments & Stripe webhooks | 20 | Pass |
| Report access control | 3 | Pass |
| Upload security | 4 | Pass |
| Validation & data tiers | 10 | Pass |
| Verification engine | 2 | Pass |
| Pilot verification rules | 4 | Pass |
| Financial calculations | 4 | Pass |
| Exports (CSV/PDF) | 3 | Pass |
| Audit delete | 3 | Pass |
| Clerk JWT | 3 | Pass |
| Registry (20 rules) | 4 | Pass |
| Summary aggregation | 6 | Pass |
| Upload cleanup | 2 | Pass |
| Scan API state machine | 4 | Pass |

---

## E2E Test Coverage Map

| User journey | Spec file |
|--------------|-----------|
| Sign-in / sign-up / protected routes | `e2e/auth.spec.ts` |
| All public pages + nav | `e2e/navigation.spec.ts` |
| CSV upload (valid, empty, malformed) | `e2e/upload.spec.ts` |
| Validation → scan → summary | `e2e/analysis.spec.ts` |
| Finding detail + leakage math | `e2e/findings.spec.ts` |
| Stripe checkout redirect + dev unlock | `e2e/payments.spec.ts` |
| IDOR + API auth | `e2e/security.spec.ts` |
| Rapid clicks, refresh, nav chaos | `e2e/stress.spec.ts` |

---

## Security Posture (Post-Fix)

| Control | Status |
|---------|--------|
| Report access requires purchase + session or ownership | Enforced |
| Credit unlock requires ownership or session | Enforced |
| Checkout requires ownership or session | Enforced |
| Audit linking cannot overwrite another user | Enforced |
| Webhook fulfillment cannot reassign owned audits | Enforced |
| Checkout status scoped to session owner | Enforced (existing) |
| Audit delete scoped to owner | Enforced (existing) |
| Stripe webhook signature verification | Enforced (existing) |
| Webhook idempotency | Enforced (existing) |
| CSV upload type/size validation | Enforced (existing) |
| Filename path traversal rejection | Enforced (new) |
| Protected routes via Clerk middleware | Enforced (E2E verified) |
| Fake report/finding URLs blocked | Enforced (E2E verified) |
| Stripe Checkout redirect for signed-in users | E2E verified |

---

## Test Commands

```bash
# API unit/integration
cd apps/api && python -m pytest tests/ -v

# Web typecheck
cd apps/web && npx tsc --noEmit

# E2E (requires API on :8000 and web on :3000, or omit PLAYWRIGHT_SKIP_WEBSERVER)
PLAYWRIGHT_SKIP_WEBSERVER=1 npx playwright test --project=chromium

# E2E with auto-start servers
npx playwright test --project=chromium
```

---

## Changelog

| Date | Action |
|------|--------|
| 2026-06-25 | Initial QA pass: 6 issues fixed, 14 new API tests, 81 total API tests passing |
| 2026-06-25 | MCP + Playwright E2E pass: 4 E2E bugs fixed, 50 browser tests passing, Clerk QA user provisioned, leakage fixtures added |
