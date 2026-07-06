#!/usr/bin/env sh
# Railway does not expand $PORT in railway.toml startCommand — must run via shell.
# Both API and worker services share apps/api/railway.toml; branch on PROCESS_ROLE
# or RAILWAY_SERVICE_NAME (name the worker service with "worker" in the name).
set -eu

role="${PROCESS_ROLE:-}"
service_name="${RAILWAY_SERVICE_NAME:-}"

case "$role" in
  worker|celery)
    echo "Starting Celery worker (PROCESS_ROLE=$role)"
    exec celery -A workers.celery_app worker -l info
    ;;
  api|web|"")
    ;;
  *)
    echo "Unknown PROCESS_ROLE=$role; starting API" >&2
    ;;
esac

if [ -z "$role" ]; then
  case "$service_name" in
    *worker*|*celery*|*Worker*|*Celery*)
      echo "Starting Celery worker (RAILWAY_SERVICE_NAME=$service_name)"
      exec celery -A workers.celery_app worker -l info
      ;;
  esac
fi

PORT="${PORT:-8000}"
echo "Starting API (RAILWAY_SERVICE_NAME=${service_name:-api})"
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
