# Production Launch Checklist

Use this checklist before promoting Revenue Leakage Radar to production traffic.

## Environment variables

- [ ] `ENVIRONMENT=production`
- [ ] `DATABASE_URL` points to production PostgreSQL
- [ ] `REDIS_URL` points to production Redis
- [ ] `WEB_URL` / `CORS_ORIGINS` set to production frontend domain
- [ ] `CLERK_SECRET_KEY` and `CLERK_JWT_ISSUER` configured
- [ ] `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`, and price IDs configured
- [ ] `SENTRY_DSN` configured (backend + frontend)
- [ ] `POSTHOG_API_KEY` and `NEXT_PUBLIC_POSTHOG_KEY` configured
- [ ] `RESEND_API_KEY` and `FROM_EMAIL` configured
- [ ] `DEV_UNLOCK_ENABLED=false`
- [ ] `CELERY_TASK_ALWAYS_EAGER=false`
- [ ] Celery worker and Redis broker running in production

## Stripe

- [ ] Webhook endpoint registered: `POST /webhooks/stripe`
- [ ] Test checkout in Stripe test mode from staging
- [ ] Verify `checkout.session.completed` unlocks report credits

## Database

- [ ] `alembic upgrade head` applied on production
- [ ] Backups enabled on PostgreSQL provider

## Smoke test (staging)

```bash
python scripts/smoke_production.py --api-url https://staging-api.example.com
```

Expected: health OK, audit completes scan, finding_count >= 20 on golden dataset.

## Observability

- [ ] Trigger a test Sentry event from staging and confirm receipt
- [ ] Confirm PostHog receives `audit_completed` or verification events
- [ ] Railway/Vercel health checks configured

## Pilot validation

- [ ] First 3 pilot customer exports manually reviewed
- [ ] CFO sign-off on evidence quality for one paid report

## Performance budgets

| Metric | Budget |
|--------|--------|
| Engine @ 1k customers | < 500ms |
| Engine @ 2k customers | < 500ms (CI gate) |
| Ingestion @ 1k rows | < 15s (CI gate) |
| Paginated findings page | < 500ms |

## Rollback

- [ ] Railway API rollback procedure documented
- [ ] Vercel frontend instant rollback tested
- [ ] Stripe webhook replay procedure understood
