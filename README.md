# Genesis

> **AI Software Engineering Operating System**

Genesis is a self-hosted, open-source platform for AI-assisted software engineering.
It provides the infrastructure, workspace management, and AI orchestration layer
for teams who want to run powerful AI development workflows on their own hardware.

---

## Current Phase: 0.3 — API Core

```
✓ Phase 0.1 — Monorepo Bootstrap    (pnpm · Turborepo · TypeScript · ESLint)
✓ Phase 0.2 — Infrastructure        (PostgreSQL · NATS · MinIO · Docker Compose)
✓ Phase 0.3 — API Core              (FastAPI · SQLModel · Alembic · JWT Auth)
  Phase 0.4 — Web & Dashboard       (Login · Projects · Workspace UI)
  Phase 1.0 — AI Integration        (Ollama · Model Router · Agents)
```

---

## Quick Start

```bash
git clone https://github.com/your-org/genesis
cd genesis

# First time setup (copies .env, checks Docker)
bash scripts/setup.sh

# Start core infrastructure (PostgreSQL · NATS · MinIO)
bash scripts/up.sh

# Start the full platform (infrastructure + API + Worker)
pnpm genesis:platform:up
```

The API will be live at **http://localhost:8080**.
Interactive docs (Swagger UI) at **http://localhost:8080/docs**.

---

## Services

| Service | Purpose | Port |
|---|---|---|
| **PostgreSQL** | Primary relational database | `5432` |
| **NATS** | Event bus / message broker (JetStream) | `4222` |
| **MinIO** | S3-compatible object storage | `9000` |
| **MinIO Console** | Web management UI | `9001` |
| **NATS Monitor** | Health & metrics | `8222` |
| **Genesis API** | FastAPI REST backend | `8080` |
| **Genesis Worker** | Async NATS-driven job processor | — |

---

## Repository Structure

```
genesis/
├── apps/
│   ├── api/          ← FastAPI REST API (Python)
│   │   ├── src/
│   │   │   ├── main.py
│   │   │   ├── core/security.py
│   │   │   └── api/routes/
│   │   │       ├── auth.py
│   │   │       ├── health.py
│   │   │       ├── workspaces.py
│   │   │       └── projects.py
│   │   └── Dockerfile
│   ├── worker/       ← Async Python worker (NATS consumer)
│   ├── web/          ← Web frontend (Phase 0.4)
│   └── dashboard/    ← System dashboard (Phase 0.4)
│
├── packages/
│   ├── db/           ← Shared Python DB package (SQLModel + Alembic)
│   │   ├── genesis_db/
│   │   │   ├── models.py
│   │   │   ├── database.py
│   │   │   └── __init__.py
│   │   └── alembic/
│   ├── cli/          ← Genesis CLI (TypeScript)
│   ├── ui/           ← Shared UI components
│   ├── sdk/          ← Client SDK
│   ├── types/        ← Shared TypeScript types
│   ├── config/       ← Shared configuration
│   └── shared/       ← Shared utilities
│
├── infrastructure/
│   ├── docker/compose/
│   │   ├── docker-compose.yml           ← Core infra (PostgreSQL, NATS, MinIO)
│   │   └── docker-compose.platform.yml  ← Platform services (API, Worker)
│   ├── postgres/     ← DB init scripts
│   ├── nats/         ← NATS config
│   └── minio/        ← MinIO config
│
├── docs/
│   ├── adr/          ← Architectural Decision Records
│   ├── rfc/          ← Request for Comments (specs)
│   ├── architecture/ ← System design documents
│   └── process.md    ← Engineering process
│
├── scripts/
│   ├── setup.sh      ← First-time setup
│   ├── up.sh         ← Start infrastructure
│   └── down.sh       ← Stop infrastructure
│
├── pyproject.toml    ← Python workspace root (uv)
├── uv.lock           ← Python lockfile
├── pyrightconfig.json← Python type checker config
└── package.json      ← JS workspace root (pnpm + Turborepo)
```

---

## Python Setup (uv)

Genesis uses [`uv`](https://github.com/astral-sh/uv) for Python package management — a single shared `.venv` at the repo root.

```bash
# Install uv (first time only)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all Python dependencies (creates .venv at repo root)
uv sync --all-packages

# Run the API locally (development)
PYTHONPATH=apps/api/src:packages/db \
  DATABASE_URL=postgresql://genesis:genesis@localhost:5432/genesis \
  uv run uvicorn main:app --reload --app-dir apps/api/src

# Run database migrations
cd packages/db
DATABASE_URL=postgresql://genesis:genesis@localhost:5432/genesis \
  uv run alembic upgrade head
```

---

## API Reference

| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | No | Health check |
| `POST` | `/api/auth/signup` | No | Register user |
| `POST` | `/api/auth/login` | No | Login, returns JWT |
| `GET` | `/api/auth/me` | JWT | Current user |
| `GET` | `/api/workspaces` | JWT | List workspaces |
| `POST` | `/api/workspaces` | JWT | Create workspace |
| `GET` | `/api/projects` | JWT | List projects |
| `POST` | `/api/projects` | JWT | Create project |
| `DELETE` | `/api/projects/{id}` | JWT | Delete project |

Full interactive docs: **http://localhost:8080/docs**

---

## Engineering Process

Every phase follows: **ADR → RFC → Implementation → Acceptance Criteria → Verification**

See [docs/process.md](docs/process.md) for the full process.

| Document | Description |
|---|---|
| [docs/infrastructure.md](docs/infrastructure.md) | Infrastructure contract |
| [docs/process.md](docs/process.md) | Engineering process |
| [docs/adr/0001-monorepo.md](docs/adr/0001-monorepo.md) | ADR: Monorepo strategy |
| [docs/adr/0003-tech-stack.md](docs/adr/0003-tech-stack.md) | ADR: Infrastructure stack |
| [docs/adr/0004-api-tech-stack.md](docs/adr/0004-api-tech-stack.md) | ADR: Python / FastAPI |
| [docs/rfc/0005-api-core-spec.md](docs/rfc/0005-api-core-spec.md) | RFC: API Core Specification |

---

## Prerequisites

| Tool | Version | Purpose |
|---|---|---|
| [Docker Desktop](https://www.docker.com/products/docker-desktop) | ≥ 4.0 | Container runtime |
| [Node.js](https://nodejs.org/) | ≥ 18 | JS tooling (pnpm, Turborepo) |
| [pnpm](https://pnpm.io/) | ≥ 9.0 | JS package manager |
| [uv](https://github.com/astral-sh/uv) | ≥ 0.12 | Python package manager |
| [Python](https://python.org) | ≥ 3.11 | API & Worker runtime |

---

## License

MIT
