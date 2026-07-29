#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
BLAZOR_DIR="$ROOT_DIR/blazor-ui"
BACKEND_VENV="$BACKEND_DIR/.venv"
BACKEND_DB="$BACKEND_DIR/local.db"

cleanup() {
  local pids=("$@")
  for pid in "${pids[@]}"; do
    if [[ -n "${pid:-}" ]] && kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
    fi
  done
}

is_running_or_external() {
  local pid="${1:-}"
  [[ -z "$pid" ]] || kill -0 "$pid" 2>/dev/null
}

trap 'cleanup "${BACKEND_PID:-}" "${BLAZOR_PID:-}"' EXIT INT TERM

if [[ ! -x "$BACKEND_VENV/bin/python" ]]; then
  if ! command -v python3 >/dev/null 2>&1; then
    echo "python3 is required to create the backend virtual environment."
    exit 1
  fi
  echo "Creating backend virtual environment..."
  python3 -m venv "$BACKEND_VENV"
  "$BACKEND_VENV/bin/pip" install -r "$BACKEND_DIR/requirements.txt"
fi

export DATABASE_URL="sqlite:///$BACKEND_DB"
export AUTO_SEED_DB="${AUTO_SEED_DB:-true}"
export PYTHONUNBUFFERED=1
export ASPNETCORE_ENVIRONMENT="${ASPNETCORE_ENVIRONMENT:-Development}"
export DOTNET_ENVIRONMENT="${DOTNET_ENVIRONMENT:-Development}"
BACKEND_URL="${BACKEND_URL:-http://127.0.0.1:8000}"
BLAZOR_URL="${BLAZOR_URL:-http://127.0.0.1:5050}"
export FRONTEND_URL="$BLAZOR_URL"
DOTNET_CMD="${DOTNET_CMD:-}"

if [[ -z "$DOTNET_CMD" ]]; then
  if command -v dotnet >/dev/null 2>&1; then
    DOTNET_CMD="$(command -v dotnet)"
  elif [[ -x "/usr/local/share/dotnet/dotnet" ]]; then
    DOTNET_CMD="/usr/local/share/dotnet/dotnet"
  elif [[ -x "/opt/homebrew/bin/dotnet" ]]; then
    DOTNET_CMD="/opt/homebrew/bin/dotnet"
  fi
fi

BACKEND_HOST="${BACKEND_URL#http://}"
BACKEND_HOST="${BACKEND_HOST#https://}"
BACKEND_HOST="${BACKEND_HOST%%/*}"
BACKEND_PORT="${BACKEND_HOST##*:}"
BACKEND_HOST="${BACKEND_HOST%:*}"
if [[ "$BACKEND_PORT" == "$BACKEND_HOST" ]]; then
  BACKEND_HOST="127.0.0.1"
  BACKEND_PORT="8000"
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:"$BACKEND_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Backend already running on $BACKEND_URL"
  BACKEND_PID=""
else
  echo "Starting backend on $BACKEND_URL"
  (cd "$BACKEND_DIR" && exec "$BACKEND_VENV/bin/python" -m uvicorn app.main:app --host "$BACKEND_HOST" --port "$BACKEND_PORT") &
  BACKEND_PID=$!
fi

if [[ -z "$DOTNET_CMD" ]]; then
  echo "dotnet is required to run the Blazor UI."
  exit 1
fi

BLAZOR_HOST="${BLAZOR_URL#http://}"
BLAZOR_HOST="${BLAZOR_HOST#https://}"
BLAZOR_HOST="${BLAZOR_HOST%%/*}"
BLAZOR_PORT="${BLAZOR_HOST##*:}"
BLAZOR_HOST="${BLAZOR_HOST%:*}"
if [[ "$BLAZOR_PORT" == "$BLAZOR_HOST" ]]; then
  BLAZOR_HOST="127.0.0.1"
  BLAZOR_PORT="5050"
fi

if command -v lsof >/dev/null 2>&1 && lsof -nP -iTCP:"$BLAZOR_PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Blazor UI already running on $BLAZOR_URL"
  BLAZOR_PID=""
else
  echo "Starting Blazor UI on $BLAZOR_URL"
  (cd "$BLAZOR_DIR" && exec "$DOTNET_CMD" run -- --urls "$BLAZOR_URL") &
  BLAZOR_PID=$!
fi

echo "Open the app at $BLAZOR_URL"

if [[ -z "${BACKEND_PID:-}" && -z "${BLAZOR_PID:-}" ]]; then
  echo "Both services are already running."
  exit 0
fi

while is_running_or_external "${BACKEND_PID:-}" && is_running_or_external "${BLAZOR_PID:-}"; do
  sleep 1
done

cleanup "${BACKEND_PID:-}" "${BLAZOR_PID:-}"
