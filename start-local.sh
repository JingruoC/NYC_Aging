#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "start-local.sh is kept for compatibility. Starting the current Blazor app with start-all.sh..."
exec bash "$ROOT_DIR/start-all.sh"
