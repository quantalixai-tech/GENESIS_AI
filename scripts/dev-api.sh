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
service_host="${GENESIS_DEV_SERVICE_HOST:-localhost}"
if [[ "$service_host" == "host.docker.internal" ]]; then
  service_host="$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' genesis-postgres)"
fi
export DATABASE_URL="postgresql://${POSTGRES_USER:-genesis}:${POSTGRES_PASSWORD:-genesis}@${service_host}:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-genesis}"

exec uv run --package api uvicorn main:app \
  --app-dir "$REPO_ROOT/apps/api/src" \
  --host 0.0.0.0 \
  --port 8080 \
  --reload-dir "$REPO_ROOT/apps/api/src" \
  --reload-dir "$REPO_ROOT/packages/db/genesis_db" \
  --reload