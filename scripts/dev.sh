#!/usr/bin/env bash

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

bash scripts/up.sh

bash scripts/dev-api.sh &
api_pid=$!
bash scripts/dev-worker.sh &
worker_pid=$!

cleanup() {
  kill "$api_pid" "$worker_pid" 2>/dev/null || true
  wait "$api_pid" "$worker_pid" 2>/dev/null || true
}

trap cleanup EXIT INT TERM
wait -n "$api_pid" "$worker_pid"