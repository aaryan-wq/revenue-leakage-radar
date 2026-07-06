#!/usr/bin/env sh
# Default concurrency=2 — Railway containers OOM if Celery auto-detects 48 CPUs.
set -eu
cd /app
export PYTHONPATH="/app${PYTHONPATH:+:$PYTHONPATH}"
CONCURRENCY="${CELERY_WORKER_CONCURRENCY:-2}"
echo "Starting Celery worker (cwd=$(pwd), concurrency=$CONCURRENCY)"
exec celery -A workers.celery_app worker -l info --concurrency "$CONCURRENCY"
