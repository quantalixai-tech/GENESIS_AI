# GENESIS AI

> **AI-Driven Software Development Platform**

GENESIS AI is a self-hosted platform that builds complete software applications from natural-language conversations. Describe what you want — the AI understands your requirements, designs the architecture, generates production-ready code, validates it automatically, and repairs failures without manual intervention.

---

## Current Phase: 0.3 — Core Platform Foundation

```
✓ Phase 0.1 — Monorepo Bootstrap    (pnpm · Turborepo · TypeScript · ESLint)
✓ Phase 0.2 — Infrastructure        (PostgreSQL · NATS · MinIO · Docker Compose)
✓ Phase 0.3 — Platform Foundation   (FastAPI · SQLModel · Alembic · JWT · AI Governance)
  Phase 0.4 — Web Application       (Auth UI · Workspace UI · Project Management)
  Phase 1.0 — AI Integration        (Ollama · Model Router · Agent Orchestration)
```

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/quantalixai-tech/GENESIS_AI
cd GENESIS_AI

# 2. First-time setup (checks Docker, creates .env)
bash scripts/setup.sh

# 3. Set your JWT_SECRET in .env (required — no default)
#    python -c "import secrets; print(secrets.token_hex(32))"

# 4. Start the full platform
docker compose up -d --build

# 5. Run database migrations
docker compose exec api sh -c "DATABASE_URL=\$DATABASE_URL alembic -c /app/packages/db/alembic.ini upgrade head"
```

**API:** http://localhost:8080 · **Swagger UI:** http://localhost:8080/docs

> For native, Docker, and DevContainer development workflows, see [docs/DEVELOPMENT.md](docs/DEVELOPMENT.md).

---

## Architecture

```
Browser / Client
     ↓
Next.js Web (port 3000)
     ↓
FastAPI REST API (port 8080)
     ↓                    ↓
PostgreSQL (5432)    NATS Event Bus (4222)
                          ↓
                    Genesis Worker
                          ↓
                    AI Agent Engine (Phase 1.0)
                          ↓
                    MinIO Object Storage (9000)
```

---

## Services

| Service | Port | Purpose |
|---|---|---|
| **Genesis API** | `8080` | FastAPI REST backend |
| **Genesis Web** | `3000` | Next.js frontend (Phase 0.4) |
| **PostgreSQL** | `5432` | Primary relational database |
| **NATS** | `4222` | Event bus / message broker |
| **MinIO** | `9000` | S3-compatible object storage |
| **MinIO Console** | `9001` | MinIO web management UI |
| **NATS Monitor** | `8222` | NATS health & metrics |

---

## Repository Structure

```
GENESIS_AI/
├── apps/
│   ├── api/          ← FastAPI backend (Python)
│   │   └── src/
│   │       ├── core/     Config, errors, logging, middleware, security
│   │       ├── api/v1/   Route handlers
│   │       ├── schemas/  API contracts
│   │       └── services/ Business logic
│   ├── web/          ← Next.js frontend
│   ├── worker/       ← NATS consumer (Python)
│   └── dashboard/    ← Admin dashboard (Phase 0.4)
├── packages/
│   ├── db/           ← Shared DB models + Alembic migrations (genesis_db)
│   ├── ui/           ← Shared React components (@genesis/ui)
│   └── cli/          ← Developer CLI (Phase 0.3+)
├── infrastructure/   ← Docker Compose, NATS config, PostgreSQL init
├── docs/             ← Architecture, ADRs, RFCs, governance
├── scripts/          ← Infrastructure lifecycle scripts
├── .devcontainer/    ← DevContainer configuration
├── docker-compose.yml ← Root convenience compose file
├── pyproject.toml    ← Python workspace (uv)
└── package.json      ← JS workspace (pnpm + Turborepo)
```

---

## API Reference

| Method | Route | Auth | Description |
|---|---|---|---|
| `GET` | `/api/health` | No | Platform health check (checks DB) |
| `POST` | `/api/v1/auth/signup` | No | Register user |
| `POST` | `/api/v1/auth/login` | No | Login, returns JWT |
| `GET` | `/api/v1/auth/me` | JWT | Current user |
| `GET` | `/api/v1/workspaces` | JWT | List workspaces |
| `POST` | `/api/v1/workspaces` | JWT | Create workspace |
| `GET` | `/api/v1/projects?workspace_id=` | JWT | List projects |
| `POST` | `/api/v1/projects` | JWT | Create project |
| `DELETE` | `/api/v1/projects/{id}` | JWT | Delete project |

Full interactive docs at **http://localhost:8080/docs** (development only).

---

## Prerequisites

| Tool | Install |
|---|---|
| Docker Desktop ≥ 4.25 | https://docker.com/products/docker-desktop |
| Node.js ≥ 18 | https://nodejs.org |
| pnpm ≥ 9 | `npm i -g pnpm@9` |
| uv ≥ 0.12 | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Python ≥ 3.11 | https://python.org |

---

## Development

See **[docs/DEVELOPMENT.md](docs/DEVELOPMENT.md)** for:
- Native development setup
- Docker development
- DevContainer development
- DevContainer CLI usage
- Database migrations
- Environment configuration
- Troubleshooting

---

## Engineering Process

Every change follows: **ADR → RFC → Implementation Plan → Code → Acceptance Criteria → Verification**

| Document | Purpose |
|---|---|
| [docs/process.md](docs/process.md) | Engineering process |
| [docs/infrastructure.md](docs/infrastructure.md) | Infrastructure contract |
| [docs/AI_GOVERNANCE.md](docs/AI_GOVERNANCE.md) | AI governance specification |
| [docs/PROJECT_AUDIT.md](docs/PROJECT_AUDIT.md) | Audit findings & priorities |
| [AGENTS.md](AGENTS.md) | Rules for AI and human developers |

---

## License

MIT
