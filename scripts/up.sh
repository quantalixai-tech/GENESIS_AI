#!/usr/bin/env bash
# =============================================================================
# Genesis — up.sh
# Start all core infrastructure services.
#
# Usage:
#   bash scripts/up.sh
#   bash scripts/up.sh --build   # rebuild images first
# =============================================================================

set -euo pipefail

# Colors
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

log_step() { echo -e "\n${BOLD}${BLUE}▶ $1${RESET}"; }
log_ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${RESET} $1"; }
log_err()  { echo -e "  ${RED}✗${RESET} $1"; }
log_info() { echo -e "  ${CYAN}→${RESET} $1"; }

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║      Genesis — Starting Services      ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
log_step "Pre-flight checks"

if ! docker info &>/dev/null 2>&1; then
  DOCKER_DESKTOP_SOCK="$HOME/.docker/run/docker.sock"
  if [ -S "$DOCKER_DESKTOP_SOCK" ] && DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCK" docker info &>/dev/null 2>&1; then
    export DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCK"
  else
    log_err "Docker daemon is not running. Start Docker Desktop first."
    exit 1
  fi
fi
log_ok "Docker is running."

if [ ! -f "$ENV_FILE" ]; then
  log_warn ".env file not found. Running setup first..."
  bash "$REPO_ROOT/scripts/setup.sh"
fi
log_ok "Environment file exists."

# ---------------------------------------------------------------------------
# Start services
# ---------------------------------------------------------------------------
log_step "Starting core infrastructure"
log_info "PostgreSQL · NATS · MinIO"

COMPOSE_ARGS=(-f "$COMPOSE_FILE" --env-file "$ENV_FILE")

# Support --build flag
if [[ "${1:-}" == "--build" ]]; then
  log_info "Building images..."
  docker compose "${COMPOSE_ARGS[@]}" build
fi

docker compose "${COMPOSE_ARGS[@]}" up -d

# ---------------------------------------------------------------------------
# Wait for health checks
# ---------------------------------------------------------------------------
log_step "Waiting for services to become healthy"

SERVICES=("genesis-postgres" "genesis-nats" "genesis-minio")
MAX_WAIT=60
INTERVAL=5

for service in "${SERVICES[@]}"; do
  elapsed=0
  printf "  Waiting for %-20s" "$service..."
  
  while [ $elapsed -lt $MAX_WAIT ]; do
    health=$(docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null || echo "not found")
    
    if [ "$health" = "healthy" ]; then
      echo -e " ${GREEN}healthy${RESET}"
      break
    elif [ "$health" = "unhealthy" ]; then
      echo -e " ${RED}unhealthy${RESET}"
      log_err "Service $service is unhealthy. Check logs: docker logs $service"
      break
    fi
    
    sleep $INTERVAL
    elapsed=$((elapsed + INTERVAL))
    printf "."
  done
  
  if [ $elapsed -ge $MAX_WAIT ]; then
    echo -e " ${YELLOW}timeout${RESET}"
    log_warn "Health check timed out for $service"
  fi
done

# ---------------------------------------------------------------------------
# Status summary
# ---------------------------------------------------------------------------
echo ""
log_step "Service endpoints"
echo ""
echo -e "  ${CYAN}PostgreSQL${RESET}   postgresql://localhost:${POSTGRES_PORT:-5432}/${POSTGRES_DB:-genesis}"
echo -e "  ${CYAN}NATS${RESET}         nats://localhost:${NATS_PORT:-4222}"
echo -e "  ${CYAN}NATS Monitor${RESET} http://localhost:${NATS_MONITORING_PORT:-8222}"
echo -e "  ${CYAN}MinIO API${RESET}    http://localhost:${MINIO_PORT:-9000}"
echo -e "  ${CYAN}MinIO Console${RESET} http://localhost:${MINIO_CONSOLE_PORT:-9001}"
echo ""
echo -e "${BOLD}${GREEN}Infrastructure is up.${RESET}"
echo ""
echo -e "  Run ${CYAN}bash scripts/down.sh${RESET} to stop."
echo -e "  Run ${CYAN}docker compose -f $COMPOSE_FILE ps${RESET} to check status."
echo ""

# Load env file for display if available
if [ -f "$ENV_FILE" ]; then
  set -a
  # shellcheck disable=SC1090
  source "$ENV_FILE" 2>/dev/null || true
  set +a
fi
