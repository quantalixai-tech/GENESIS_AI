#!/usr/bin/env bash
# =============================================================================
# Genesis — clean.sh
# ⚠️  DESTRUCTIVE: Stop all services and remove all data volumes.
#
# This will permanently delete:
#   - All PostgreSQL data
#   - All MinIO objects
#   - All NATS JetStream data
#
# Usage:
#   bash scripts/clean.sh
#   bash scripts/clean.sh --force   # skip confirmation prompt
# =============================================================================

set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
BOLD='\033[1m'
RESET='\033[0m'

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COMPOSE_FILE="$REPO_ROOT/infrastructure/docker/compose/docker-compose.yml"
ENV_FILE="$REPO_ROOT/.env"

echo ""
echo -e "${BOLD}╔══════════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║  ${RED}⚠  Genesis — Clean (DESTRUCTIVE)  ⚠${RESET}${BOLD}  ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════════╝${RESET}"
echo ""
echo -e "  ${RED}This will permanently delete all data volumes:${RESET}"
echo -e "  ${YELLOW}→${RESET} postgres-data (all database records)"
echo -e "  ${YELLOW}→${RESET} minio-data    (all stored artifacts)"
echo -e "  ${YELLOW}→${RESET} nats-data     (all JetStream streams)"
echo ""

# ---------------------------------------------------------------------------
# Confirmation (unless --force)
# ---------------------------------------------------------------------------
if [[ "${1:-}" != "--force" ]]; then
  read -r -p "  Type 'yes' to confirm: " confirmation
  if [[ "$confirmation" != "yes" ]]; then
    echo ""
    echo -e "  ${GREEN}Aborted.${RESET} No data was deleted."
    echo ""
    exit 0
  fi
fi

echo ""
echo -e "  ${BLUE}▶${RESET} Stopping and removing all volumes..."

COMPOSE_ARGS=(-f "$COMPOSE_FILE")
if [ -f "$ENV_FILE" ]; then
  COMPOSE_ARGS+=(--env-file "$ENV_FILE")
fi

docker compose "${COMPOSE_ARGS[@]}" down --volumes --remove-orphans

echo ""
echo -e "${BOLD}${GREEN}Clean complete.${RESET} All volumes removed."
echo ""
echo -e "  Run ${CYAN}bash scripts/up.sh${RESET} to start fresh."
echo ""
