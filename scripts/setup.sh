#!/usr/bin/env bash
# =============================================================================
# Genesis — setup.sh
# First-time environment setup for local development.
#
# What this does:
#   1. Verifies Docker is installed and running
#   2. Creates .env from .env.example if it doesn't exist
#   3. Confirms the infrastructure compose file exists
#
# Usage:
#   bash scripts/setup.sh
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

# ---------------------------------------------------------------------------
log_step() { echo -e "\n${BOLD}${BLUE}▶ $1${RESET}"; }
log_ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${RESET} $1"; }
log_err()  { echo -e "  ${RED}✗${RESET} $1"; }
log_info() { echo -e "  ${CYAN}→${RESET} $1"; }
# ---------------------------------------------------------------------------

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║        Genesis — Setup                ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

# ---------------------------------------------------------------------------
# Step 1: Check Docker
# ---------------------------------------------------------------------------
log_step "Checking Docker"

if ! command -v docker &>/dev/null; then
  log_err "Docker is not installed."
  log_info "Install Docker Desktop: https://www.docker.com/products/docker-desktop"
  exit 1
fi
log_ok "Docker found: $(docker --version)"

# On macOS with Docker Desktop, the socket may be at a non-default path
if ! docker info &>/dev/null 2>&1; then
  # Try the Docker Desktop socket explicitly
  DOCKER_DESKTOP_SOCK="$HOME/.docker/run/docker.sock"
  if [ -S "$DOCKER_DESKTOP_SOCK" ] && DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCK" docker info &>/dev/null 2>&1; then
    export DOCKER_HOST="unix://$DOCKER_DESKTOP_SOCK"
    log_warn "Using Docker Desktop socket: $DOCKER_HOST"
    log_info "Consider setting DOCKER_HOST in your shell profile."
  else
    log_err "Docker daemon is not running. Please start Docker Desktop."
    exit 1
  fi
fi
log_ok "Docker daemon is running."

# ---------------------------------------------------------------------------
# Step 2: Check Docker Compose
# ---------------------------------------------------------------------------
log_step "Checking Docker Compose"

if ! docker compose version &>/dev/null; then
  log_err "Docker Compose (v2) is not available."
  log_info "Update Docker Desktop to get Compose v2."
  exit 1
fi
log_ok "Docker Compose found: $(docker compose version --short)"

# ---------------------------------------------------------------------------
# Step 3: Create .env file
# ---------------------------------------------------------------------------
log_step "Setting up environment file"

ENV_FILE="$REPO_ROOT/.env"
ENV_EXAMPLE="$REPO_ROOT/.env.example"

if [ ! -f "$ENV_EXAMPLE" ]; then
  log_err ".env.example not found at $ENV_EXAMPLE"
  exit 1
fi

if [ -f "$ENV_FILE" ]; then
  log_warn ".env already exists — skipping. Edit it manually if needed."
else
  cp "$ENV_EXAMPLE" "$ENV_FILE"
  log_ok ".env created from .env.example"
  log_warn "Review $ENV_FILE and update any credentials before starting."
fi

# ---------------------------------------------------------------------------
# Step 4: Verify compose file
# ---------------------------------------------------------------------------
log_step "Verifying infrastructure"

if [ ! -f "$COMPOSE_FILE" ]; then
  log_err "Docker Compose file not found: $COMPOSE_FILE"
  exit 1
fi
log_ok "Docker Compose file found."

# Validate compose syntax
if docker compose -f "$COMPOSE_FILE" config --quiet 2>/dev/null; then
  log_ok "Docker Compose configuration is valid."
else
  log_warn "Could not validate Compose config (may need .env file). Continuing."
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${GREEN}Setup complete.${RESET}"
echo ""
echo -e "  Run ${CYAN}bash scripts/up.sh${RESET} to start the infrastructure."
echo -e "  Run ${CYAN}bash scripts/down.sh${RESET} to stop it."
echo ""
