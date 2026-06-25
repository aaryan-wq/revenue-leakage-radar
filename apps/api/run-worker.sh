#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"

if [[ ! -f .venv/bin/celery ]]; then
  echo "Virtualenv not found. Run: python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt" >&2
  exit 1
fi

exec .venv/bin/celery -A workers.celery_app worker -l info "$@"
