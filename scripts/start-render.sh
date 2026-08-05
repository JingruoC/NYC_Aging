#!/usr/bin/env bash
set -euo pipefail

PORT="${PORT:-10000}"
BACKEND_PORT="${BACKEND_PORT:-8000}"

export AUTO_SEED_DB="${AUTO_SEED_DB:-true}"
export DATABASE_URL="${DATABASE_URL:-sqlite:////tmp/simple-servings.db}"
export FRONTEND_URL="${FRONTEND_URL:-http://127.0.0.1:${PORT}}"
export PYTHONPATH="${PYTHONPATH:-/app/backend}"
export PythonApi__BaseUrl="${PythonApi__BaseUrl:-http://127.0.0.1:${BACKEND_PORT}}"

cleanup() {
  if [[ -n "${BACKEND_PID:-}" ]] && kill -0 "$BACKEND_PID" 2>/dev/null; then
    kill "$BACKEND_PID" 2>/dev/null || true
  fi
}

trap cleanup EXIT INT TERM

cd /app/backend
/app/backend/.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port "$BACKEND_PORT" &
BACKEND_PID=$!

BACKEND_READY=0
for _ in $(seq 1 30); do
  if /app/backend/.venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:${BACKEND_PORT}/health', timeout=2).read()" >/dev/null 2>&1; then
    BACKEND_READY=1
    break
  fi
  sleep 1
done

if [[ "$BACKEND_READY" != "1" ]]; then
  echo "FastAPI backend did not become healthy."
  exit 1
fi

cd /app/blazor
exec dotnet NycAging.Web.dll --urls "http://0.0.0.0:${PORT}"
