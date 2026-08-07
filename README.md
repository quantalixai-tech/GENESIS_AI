# Genesis

> **AI Software Engineering Operating System**

Genesis is a self-hosted, open-source platform for AI-assisted software engineering.
It provides the infrastructure, workspace management, and AI orchestration layer
for teams who want to run powerful AI development workflows on their own hardware.

---

## Current Phase: 0.2 — Infrastructure Bootstrap

**Phase 0 is the Operating System phase.**
The objective is not to build AI. The objective is to build the foundation on which every future AI capability will run.

```
✓ Phase 0.1 — Monorepo Bootstrap    (pnpm · Turborepo · TypeScript · ESLint)
✓ Phase 0.2 — Infrastructure        (PostgreSQL · NATS · MinIO · Docker Compose)
  Phase 0.3 — API Core              (REST API · Auth · DB migrations)
  Phase 0.4 — Web & Dashboard       (Login · Projects · Workspace UI)
  Phase 1.0 — AI Integration        (Ollama · Model Router · Agents)
```

---

## Quick Start

```bash
git clone https://github.com/your-org/genesis
cd genesis

# First time setup
bash scripts/setup.sh

# Start core infrastructure (PostgreSQL · NATS · MinIO)
bash scripts/up.sh

# Stop infrastructure (data preserved)
bash scripts/down.sh
```

Or via pnpm:

```bash
pnpm genesis:setup
pnpm genesis:up
pnpm genesis:down
```

---

## Infrastructure

| Service | Purpose | Port |
|---|---|---|
| PostgreSQL | Primary database | `5432` |
| NATS | Event bus / message broker | `4222` |
| MinIO | S3-compatible object storage | `9000` |
| MinIO Console | Web management UI | `9001` |
| NATS Monitor | Health monitoring | `8222` |

See [docs/infrastructure.md](docs/infrastructure.md) for the full infrastructure contract.

---

## Repository Structure

```
genesis/
├── apps/
│   ├── api/          ← REST API (Phase 0.3)
│   ├── web/          ← Web frontend (Phase 0.4)
│   ├── worker/       ← Background job processor (Phase 0.3)
│   └── dashboard/    ← System dashboard (Phase 0.4)
│
├── packages/
│   ├── cli/          ← Genesis CLI (`genesis` command)
│   ├── ui/           ← Shared UI components
│   ├── sdk/          ← Client SDK
│   ├── types/        ← Shared TypeScript types
│   ├── config/       ← Shared configuration
│   └── shared/       ← Shared utilities
│
├── infrastructure/
│   ├── docker/compose/  ← Docker Compose files
│   ├── postgres/        ← DB init scripts
│   ├── nats/            ← NATS server config
│   └── minio/           ← MinIO config
│
├── docs/
│   ├── adr/          ← Architectural Decision Records
│   ├── rfc/          ← Request for Comments (specs)
│   ├── architecture/ ← System design documents
│   └── process.md    ← Engineering process
│
└── scripts/
    ├── setup.sh      ← First-time setup
    ├── up.sh         ← Start infrastructure
    ├── down.sh       ← Stop infrastructure
    ├── restart.sh    ← Restart infrastructure
    └── clean.sh      ← Reset everything (destructive)
```

---

## Engineering Process

Every phase follows: **ADR → RFC → Implementation → Acceptance Criteria → Verification**

See [docs/process.md](docs/process.md) for the full engineering process.

| Type | Location | Purpose |
|---|---|---|
| ADR | `docs/adr/` | *Why* an architectural decision was made |
| RFC | `docs/rfc/` | *What* exactly we're building (technical spec) |

---

## Documentation Index

| Document | Description |
|---|---|
| [docs/infrastructure.md](docs/infrastructure.md) | Infrastructure contract (ports, services, volumes) |
| [docs/process.md](docs/process.md) | Engineering process |
| [docs/architecture/vision.md](docs/architecture/vision.md) | Product vision |
| [docs/architecture/system-overview.md](docs/architecture/system-overview.md) | System architecture |
| [docs/architecture/roadmap.md](docs/architecture/roadmap.md) | Development roadmap |
| [docs/adr/0001-monorepo.md](docs/adr/0001-monorepo.md) | ADR: Monorepo strategy |
| [docs/adr/0002-branching.md](docs/adr/0002-branching.md) | ADR: Branching strategy |
| [docs/adr/0003-tech-stack.md](docs/adr/0003-tech-stack.md) | ADR: Core infrastructure stack |
| [docs/rfc/0001-apfs.md](docs/rfc/0001-apfs.md) | RFC: AI Project File System |
| [docs/rfc/0004-health.md](docs/rfc/0004-health.md) | RFC: Health check specification |

---

## Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop) ≥ 4.0
- [Node.js](https://nodejs.org/) ≥ 18
- [pnpm](https://pnpm.io/) ≥ 9.0

---

## License

MIT
