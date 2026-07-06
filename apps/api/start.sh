#!/usr/bin/env sh
# Railway does not expand $PORT in railway.toml startCommand — must run via shell.
set -eu
PORT="${PORT:-8000}"
exec uvicorn main:app --host 0.0.0.0 --port "$PORT"
