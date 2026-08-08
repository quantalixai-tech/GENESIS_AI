# GENESIS AI Development Guide

> Complete guide to setting up and running GENESIS AI locally.

---

## Prerequisites

| Tool                                                             | Version | Purpose                | Install                                            |
| ---------------------------------------------------------------- | ------- | ---------------------- | -------------------------------------------------- |
| [Docker Desktop](https://www.docker.com/products/docker-desktop) | ≥ 4.25  | Container runtime      | Required                                           |
| [Node.js](https://nodejs.org/)                                   | ≥ 18    | JS tooling             | Required                                           |
| [pnpm](https://pnpm.io/)                                         | ≥ 9.0   | JS package manager     | `npm i -g pnpm@9`                                  |
| [uv](https://github.com/astral-sh/uv)                            | ≥ 0.12  | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| [Python](https://python.org)                                     | ≥ 3.11  | API & Worker runtime   | Required                                           |

**Optional (for DevContainer development):**

- [VS Code](https://code.visualstudio.com/) + [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- [DevContainer CLI](https://github.com/devcontainers/cli): `npm i -g @devcontainers/cli`

---

## Quick Start (Docker — Recommended)

```bash
# 1. Clone
git clone https://github.com/quantalixai-tech/GENESIS_AI
cd GENESIS_AI

# 2. First-time setup (checks Docker, creates .env)
bash scripts/setup.sh

# 3. Edit .env and set JWT_SECRET
#    python -c "import secrets; print(secrets.token_hex(32))"
nano .env

# 4. Start everything (infra + API + Worker)
docker compose up -d --build

# 5. Run database migrations
docker compose exec api sh -c "cd /app && alembic -c packages/db/alembic.ini upgrade head"
```

The platform is now running:

| Service            | URL                        |
| ------------------ | -------------------------- |
| API                | http://localhost:8080      |
| API Docs (Swagger) | http://localhost:8080/docs |
| MinIO Console      | http://localhost:9001      |
| NATS Monitor       | http://localhost:8222      |

---

## Native Development (no Docker for Python)

Run the API and Worker directly on your machine, with infrastructure in Docker.

```bash
# 1. Install dependencies
pnpm install            # JS packages
uv sync --all-packages  # Python packages

# 2. Copy .env and set JWT_SECRET
cp .env.example .env
# Edit .env — set JWT_SECRET

# 3. Start infrastructure only
pnpm genesis:up
# or: bash scripts/up.sh

# 4. Run database migrations
cd packages/db
DATABASE_URL=postgresql://genesis:genesis@localhost:5432/genesis \
  uv run alembic upgrade head
cd ../..

# 5. Start the API (hot reload)
PYTHONPATH=apps/api/src:packages/db \
  uv run uvicorn main:app \
  --reload \
  --app-dir apps/api/src \
  --port 8080

# 6. Start the Worker (separate terminal)
PYTHONPATH=apps/worker/src:packages/db \
  uv run python apps/worker/src/main.py

# 7. Start the web frontend (separate terminal)
pnpm dev
```

---

## DevContainer Development

The repository includes a full DevContainer configuration that provides a pre-configured environment with Node.js, Python, and Docker-in-Docker.

### Using VS Code

1. Open the repository in VS Code
2. When prompted, click **"Reopen in Container"**
3. Wait for the container to build (~2 min first time)
4. The `post-create.sh` script runs automatically and installs all dependencies

### Using DevContainer CLI

```bash
# Install the CLI
npm i -g @devcontainers/cli

# Build the container image
devcontainer build --workspace-folder .

# Start the container
devcontainer up --workspace-folder .

# Run a command inside the container
devcontainer exec --workspace-folder . pnpm install
devcontainer exec --workspace-folder . bash scripts/setup.sh

# Open a shell inside the container
devcontainer exec --workspace-folder . bash
```

### Inside the DevContainer

Once inside, the full development environment is available:

```bash
# Start infrastructure
pnpm genesis:up

# Start the recommended live-development backend
pnpm genesis:dev

# Run migrations
cd packages/db && DATABASE_URL=postgresql://genesis:genesis@localhost:5432/genesis \
  uv run alembic upgrade head

# Or run the API and Worker in separate terminals
pnpm genesis:dev:api
pnpm genesis:dev:worker

# Start web
pnpm dev
```

---

## Environment Setup

All environment variables are documented in [`.env.example`](../.env.example).

### Required

| Variable     | Description                                                                                              |
| ------------ | -------------------------------------------------------------------------------------------------------- |
| `JWT_SECRET` | JWT signing secret. **No default.** Generate: `python -c "import secrets; print(secrets.token_hex(32))"` |

### Database

| Variable            | Default                                               | Description                             |
| ------------------- | ----------------------------------------------------- | --------------------------------------- |
| `DATABASE_URL`      | `postgresql://genesis:genesis@localhost:5432/genesis` | Full PostgreSQL connection string       |
| `POSTGRES_DB`       | `genesis`                                             | Database name (Docker Compose only)     |
| `POSTGRES_USER`     | `genesis`                                             | Database user (Docker Compose only)     |
| `POSTGRES_PASSWORD` | `genesis`                                             | Database password (Docker Compose only) |

### Platform

| Variable                      | Default                 | Description                                           |
| ----------------------------- | ----------------------- | ----------------------------------------------------- |
| `GENESIS_ENV`                 | `development`           | Environment: `development` / `staging` / `production` |
| `GENESIS_LOG_LEVEL`           | `info`                  | Log level: `debug` / `info` / `warning` / `error`     |
| `CORS_ORIGINS`                | `http://localhost:3000` | Comma-separated allowed CORS origins                  |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                    | JWT token lifetime in minutes                         |

---

## Database Migrations

```bash
# Apply all pending migrations
cd packages/db
DATABASE_URL=<your-url> uv run alembic upgrade head

# Check migration status
DATABASE_URL=<your-url> uv run alembic current

# Create a new migration
DATABASE_URL=<your-url> uv run alembic revision --autogenerate -m "description"

# Rollback one migration
DATABASE_URL=<your-url> uv run alembic downgrade -1
```

---

## Canonical Commands

### JavaScript / TypeScript

```bash
pnpm install          # Install all JS/TS dependencies
pnpm dev              # Start Next.js in development mode
pnpm build            # Build all packages
pnpm lint             # ESLint across all packages
pnpm check-types      # TypeScript type checking
pnpm typecheck        # Alias for check-types
pnpm format           # Prettier format all files
pnpm format:check     # Prettier check (no writes)
pnpm test             # Run tests (when implemented)
pnpm clean            # Remove build artifacts
```

### Python

```bash
uv sync --all-packages       # Install all Python dependencies
uv run ruff format .         # Format Python code
uv run ruff check .          # Lint Python code
uv run mypy apps/api/src packages/db  # Type check
uv run pytest                # Run tests (when implemented)
```

### Infrastructure

```bash
pnpm genesis:setup           # First-time setup (check Docker, copy .env)
pnpm genesis:up              # Start core infrastructure
pnpm genesis:down            # Stop core infrastructure
pnpm genesis:restart         # Restart core infrastructure
pnpm genesis:platform:up     # Start full platform (infra + API + Worker)
pnpm genesis:platform:down   # Stop full platform
pnpm genesis:logs            # Follow all logs

# Or using the convenience root compose:
docker compose up -d --build # Start everything
docker compose down          # Stop everything
docker compose logs -f       # Follow all logs
```

---

## Testing

Tests are planned but not yet implemented. The test pipeline is ready:

```bash
pnpm test            # Runs turbo test task across all packages
uv run pytest        # Python tests (when tests/ dirs are added)
```

---

## Linting & Formatting

```bash
# TypeScript
pnpm lint            # ESLint (0 warnings allowed)
pnpm format          # Prettier (writes files)
pnpm format:check    # Prettier (check only, for CI)

# Python
uv run ruff format . # Format
uv run ruff check .  # Lint
```

---

## Troubleshooting

### `pydantic_settings` not found

```bash
uv sync --all-packages
```

The `.venv` was created before `pydantic-settings` was added to `apps/api/pyproject.toml`. Re-syncing installs it.

### Docker daemon not running

Start Docker Desktop and ensure the socket is accessible:

```bash
docker info  # should print Docker info
```

### Port already in use

Check what's using the port:

```bash
lsof -i :8080   # API port
lsof -i :5432   # PostgreSQL port
```

### JWT_SECRET not set

The API will refuse to start without `JWT_SECRET`. Generate one and add it to `.env`:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

### Database migration fails

Ensure the database is running and the `DATABASE_URL` is correct:

```bash
pnpm genesis:up  # starts PostgreSQL
psql postgresql://genesis:genesis@localhost:5432/genesis -c "SELECT 1"
```

### VS Code shows `pydantic_settings` import error after `uv sync`

Restart the Python language server: **Cmd+Shift+P → "Python: Restart Language Server"**

---

## Repository Structure

```
GENESIS_AI/
├── apps/
│   ├── api/                  FastAPI backend (Python)
│   │   └── src/
│   │       ├── main.py       Application entry point
│   │       ├── core/         Config, errors, logging, middleware, security
│   │       ├── api/v1/       Versioned route handlers (thin — no business logic)
│   │       ├── schemas/      API request/response contracts
│   │       └── services/     Business logic layer
│   ├── web/                  Next.js frontend
│   ├── worker/               NATS message consumer (Python)
│   └── dashboard/            Admin dashboard (Phase 0.4)
├── packages/
│   ├── db/                   Shared Python DB package (SQLModel + Alembic)
│   │   └── genesis_db/       Models: User, Workspace, Project, governance tables
│   ├── ui/                   Shared React UI components (@genesis/ui)
│   ├── cli/                  Genesis CLI (TypeScript, Phase 0.3+)
│   ├── eslint-config/        Shared ESLint configuration
│   └── typescript-config/    Shared TypeScript configuration
├── infrastructure/
│   ├── docker/compose/       Docker Compose files (layered)
│   ├── postgres/             DB initialization SQL
│   ├── nats/                 NATS configuration
│   └── minio/                MinIO configuration
├── docs/
│   ├── adr/                  Architectural Decision Records
│   ├── rfc/                  Request for Comments
│   ├── architecture/         System design documents
│   ├── AI_GOVERNANCE.md      AI governance specification
│   ├── PROJECT_AUDIT.md      Audit findings
│   └── DEVELOPMENT.md        ← this file
├── scripts/                  Infrastructure lifecycle scripts
├── .devcontainer/            DevContainer configuration
├── docker-compose.yml        Root convenience compose (includes infra + platform)
├── pyproject.toml            Python workspace root (uv)
├── package.json              JS workspace root (pnpm + Turborepo)
├── AGENTS.md                 Rules for AI and human developers
└── README.md                 Project overview and quick start
```

---

## See Also

- [AGENTS.md](../AGENTS.md) — Engineering rules for AI and human developers
- [docs/AI_GOVERNANCE.md](AI_GOVERNANCE.md) — AI governance specification
- [docs/infrastructure.md](infrastructure.md) — Infrastructure contract
- [docs/process.md](process.md) — Engineering process
- [docs/PROJECT_AUDIT.md](PROJECT_AUDIT.md) — Audit findings and known issues
