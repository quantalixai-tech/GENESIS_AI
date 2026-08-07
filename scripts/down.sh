#!/usr/bin/env bash
# =============================================================================
# Genesis — down.sh
# Stop all core infrastructure services (preserves volumes and data).
#
# Usage:
#   bash scripts/down.sh
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/infrastructure/docker/compose/docker-compose.yml"
ENV_FILE="$REPO_ROOT/.env"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║      Genesis — Stopping Services      ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

if ! docker info &>/dev/null 2>&1; then
  DOCKER_DESKTOP_SOCK="$HOME/.docker/run/docker.sock"
  if [ -S "$DOCKER_DESKTOP_SOCK" ] && DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCK" docker info &>/dev/null 2>&1; then
    export DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCK"
  else
    echo -e "  ${RED}✗${RESET} Docker is not running."
    exit 1
  fi
fi

COMPOSE_ARGS=(-f "$COMPOSE_FILE")
if [ -f "$ENV_FILE" ]; then
  COMPOSE_ARGS+=(--env-file "$ENV_FILE")
fi

docker compose "${COMPOSE_ARGS[@]}" down

echo ""
echo -e "${BOLD}${GREEN}Infrastructure stopped.${RESET} (Data volumes preserved)"
echo ""
echo -e "  Run ${CYAN}bash scripts/up.sh${RESET} to start again."
echo -e "  Run ${CYAN}bash scripts/clean.sh${RESET} to remove volumes (destructive)."
echo ""
