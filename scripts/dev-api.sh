#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

if [[ -f .env ]]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi

export PYTHONPATH="$REPO_ROOT/apps/api/src:$REPO_ROOT/packages/db${PYTHONPATH:+:$PYTHONPATH}"
export DATABASE_URL="postgresql://${POSTGRES_USER:-genesis}:${POSTGRES_PASSWORD:-genesis}@${GENESIS_DEV_SERVICE_HOST:-localhost}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-genesis}"

exec uv run --package api uvicorn main:app \
  --app-dir "$REPO_ROOT/apps/api/src" \
  --host 0.0.0.0 \
  --port 8080 \
  --reload