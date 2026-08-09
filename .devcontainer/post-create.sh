#!/usr/bin/env bash
# =============================================================================
# Genesis — DevContainer post-create.sh
# Runs automatically after the container is created via postCreateCommand.
# Called as: bash /workspace/.devcontainer/post-create.sh
#
# What this does:
#   1. Installs Node.js dependencies (pnpm install)
#   2. Builds the genesis CLI
#   3. Installs the CLI as a global 'genesis' command (/usr/local/bin/genesis)
#   4. Installs Python dependencies (uv sync --all-packages --dev)
#   5. Creates .env with a generated JWT_SECRET if not present
#   6. Prints getting-started summary
# =============================================================================

set -euo pipefail

# Always work from workspace root (postCreateCommand CWD may vary)
cd /workspace

RESET='\033[0m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
BOLD='\033[1m'

log_ok()   { echo -e "  ${GREEN}✓${RESET} $1"; }
log_info() { echo -e "  ${CYAN}→${RESET} $1"; }
log_warn() { echo -e "  ${YELLOW}⚠${RESET} $1"; }

echo ""
echo -e "${BOLD}╔══════════════════════════════════════╗${RESET}"
echo -e "${BOLD}║    GENESIS AI — DevContainer Setup   ║${RESET}"
echo -e "${BOLD}╚══════════════════════════════════════╝${RESET}"
echo ""

# ---------------------------------------------------------------------------
# 0. Core tools installation (pnpm, uv)
# ---------------------------------------------------------------------------
log_info "Installing pnpm globally..."
npm install -g pnpm@9
log_ok "pnpm installed"

log_info "Installing uv (Python packaging in Rust)..."
curl -LsSf https://astral.sh/uv/install.sh | sh
log_ok "uv installed"

# ---------------------------------------------------------------------------
# Ensure uv is on PATH (installed by curl script into ~/.local/bin)
# The home dir may be /root or /home/vscode depending on the image user
# ---------------------------------------------------------------------------
export PATH="$HOME/.local/bin:/root/.local/bin:/home/vscode/.local/bin:$PATH"

# ---------------------------------------------------------------------------
# 1. pnpm install
# ---------------------------------------------------------------------------
log_info "Installing Node.js dependencies..."
pnpm install
log_ok "Node.js dependencies installed"

# ---------------------------------------------------------------------------
# 2. Build genesis CLI
# ---------------------------------------------------------------------------
log_info "Building genesis CLI..."
pnpm --filter @genesis/cli build
log_ok "CLI built (packages/cli/dist/index.js)"

# ---------------------------------------------------------------------------
# 3. Install genesis as a global command
#    Creates /usr/local/bin/genesis → /workspace/packages/cli/dist/index.js
#    This makes 'genesis' work as a bare command in any terminal session.
# ---------------------------------------------------------------------------
log_info "Installing genesis as global command..."

# Ensure the dist file has the executable shebang
CLI_DIST="/workspace/packages/cli/dist/index.js"
chmod +x "$CLI_DIST"

# Write a bash exec wrapper — most reliable, avoids any ESM/CJS issues
cat << 'EOF' | sudo tee /usr/local/bin/genesis > /dev/null
#!/usr/bin/env bash
exec node /workspace/packages/cli/dist/index.js "$@"
EOF
sudo chmod +x /usr/local/bin/genesis
log_ok "'genesis' command available globally"

# ---------------------------------------------------------------------------
# 4. Python dependencies
# ---------------------------------------------------------------------------
log_info "Installing Python dependencies (uv sync --all-packages --dev)..."
uv sync --all-packages --dev
log_ok "Python dependencies installed"

# ---------------------------------------------------------------------------
# 5. .env bootstrap
# ---------------------------------------------------------------------------
if [ ! -f ".env" ]; then
  log_info "Creating .env with generated JWT_SECRET..."
  cp .env.example .env
  # Generate a cryptographically secure 64-character hex secret using Python stdlib
  JWT_SECRET=$(python3 -c "import secrets; print(secrets.token_hex(32))")
  # Replace the JWT_SECRET= line (or append if missing)
  if grep -q "^JWT_SECRET=" .env; then
    sed -i "s/^JWT_SECRET=.*/JWT_SECRET=${JWT_SECRET}/" .env
  else
    echo "JWT_SECRET=${JWT_SECRET}" >> .env
  fi
  log_ok ".env created with generated JWT_SECRET"

else
  log_ok ".env already exists"
fi

# ---------------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------------
echo ""
echo -e "${BOLD}${GREEN}DevContainer ready.${RESET}"
echo ""
echo -e "  ${BOLD}Quick start (run in this terminal):${RESET}"
echo -e "  ${CYAN}genesis start${RESET}     — Start core infra (postgres, nats, minio)"
echo -e "  ${CYAN}genesis migrate${RESET}   — Apply database migrations"
echo -e "  ${CYAN}genesis dev${RESET}       — Start API + web with hot-reload"
echo -e "  ${CYAN}genesis status${RESET}    — Check service health"
echo -e "  ${CYAN}genesis doctor${RESET}    — Run platform health checks"
echo -e "  ${CYAN}genesis --help${RESET}    — All commands"
echo ""
