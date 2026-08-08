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

export PYTHONPATH="$REPO_ROOT/apps/worker/src:$REPO_ROOT/packages/db${PYTHONPATH:+:$PYTHONPATH}"
export DATABASE_URL="postgresql://${POSTGRES_USER:-genesis}:${POSTGRES_PASSWORD:-genesis}@${GENESIS_DEV_SERVICE_HOST:-localhost}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-genesis}"
export NATS_URL="nats://${GENESIS_DEV_SERVICE_HOST:-localhost}:${NATS_PORT:-4222}"

exec uv run --package worker python "$REPO_ROOT/apps/worker/src/main.py"