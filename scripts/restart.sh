#!/usr/bin/env bash
# =============================================================================
# Genesis — restart.sh
# Restart all core infrastructure services.
#
# Usage:
#   bash scripts/restart.sh
# =============================================================================

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

BOLD='\033[1m'
BLUE='\033[0;34m'
RESET='\033[0m'

echo ""
echo -e "${BOLD}${BLUE}▶ Restarting Genesis infrastructure...${RESET}"
echo ""

bash "$REPO_ROOT/scripts/down.sh"
bash "$REPO_ROOT/scripts/up.sh"
