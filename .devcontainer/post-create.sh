#!/usr/bin/env bash
# =============================================================================
# Genesis — DevContainer post-create.sh
# Runs automatically after the container is created.
#
# What this does:
#   1. Installs Node.js (pnpm) dependencies
#   2. Installs Python (uv) dependencies
#   3. Copies .env.example to .env if .env doesn't exist
#   4. Prints a getting-started summary
# =============================================================================

set -euo pipefail

RESET='\033[0m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
BOLD='\033[1m'

log_ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
log_info() { echo -e "  ${CYAN}→${RESET} $1"; }

echo ""
echo -e "${BOLD}GENESIS AI — DevContainer Setup${RESET}"
echo ""

# ---------------------------------------------------------------------------
# 1. pnpm install
# ---------------------------------------------------------------------------
log_info "Installing Node.js dependencies (pnpm install)..."
pnpm install --frozen-lockfile
log_ok "Node.js dependencies installed"

# ---------------------------------------------------------------------------
# 2. uv sync
# ---------------------------------------------------------------------------
# Ensure uv is on PATH (installed by onCreateCommand)
export PATH="$HOME/.local/bin:$PATH"

log_info "Installing Python dependencies (uv sync --all-packages)..."
uv sync --all-packages
log_ok "Python dependencies installed"

# ---------------------------------------------------------------------------
# 3. .env bootstrap
# ---------------------------------------------------------------------------
if [ ! -f ".env" ]; then
  cp .env.example .env
  log_ok ".env created from .env.example"
  echo ""
  echo -e "  ${CYAN}⚠${RESET}  Review .env and set JWT_SECRET before starting the API."
else
  log_ok ".env already exists"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${GREEN}DevContainer ready.${RESET}"
echo ""
echo -e "  ${CYAN}pnpm dev${RESET}            — Start Next.js web frontend"
echo -e "  ${CYAN}pnpm genesis:up${RESET}     — Start infrastructure (PostgreSQL, NATS, MinIO)"
echo -e "  ${CYAN}pnpm genesis:dev${RESET}    — Start infrastructure, API reload, and Worker"
echo -e "  ${CYAN}pnpm genesis:dev:api${RESET} — Start API with hot reload"
echo -e "  ${CYAN}pnpm genesis:dev:worker${RESET} — Start Worker locally"
echo -e "  ${CYAN}pnpm genesis:platform:up${RESET} — Start full platform (infra + API + Worker)"
echo ""
