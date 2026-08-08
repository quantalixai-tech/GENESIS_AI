# GENESIS AI — Agent Development Rules

**Version:** 1.0.0
**Status:** Active
**Applies to:** All coding agents, AI assistants, and human developers working on this repository.

> These rules exist to preserve architecture integrity, security, and governance as the codebase grows. They are strict by design. Deviation requires explicit justification documented in an ADR.

---

## Engineering Process

Every non-trivial change follows the process defined in `docs/process.md`:

```
ADR → RFC → Implementation Plan → Code → Acceptance Criteria → Verification
```

- ADRs document *why* an architectural decision was made.
- RFCs define *what* is being built before any code is written.
- Implementation plan breaks the RFC into ordered file changes.
- Verification proves acceptance criteria are met.

Do not skip steps. Do not write code before the RFC is accepted.

---

## Before Coding

Before writing or modifying any code, you MUST:

1. **Read relevant documentation.**
   - `docs/process.md` — engineering process
   - `docs/infrastructure.md` — infrastructure contract
   - `docs/AI_GOVERNANCE.md` — AI governance rules
   - `docs/PROJECT_AUDIT.md` — known issues and priorities
   - Relevant ADRs in `docs/adr/`
   - Relevant RFCs in `docs/rfc/`

2. **Inspect existing implementations.**
   - Search for existing services, utilities, and patterns before creating new ones.
   - Run `grep -r "function_name" --include="*.py"` before declaring something doesn't exist.
   - Check `packages/db/genesis_db/` for existing models before defining new ones.

3. **Understand architectural boundaries.**
   ```
   Route Handler  →  Service  →  Repository/DB
                              →  External Service
   ```
   - Route handlers: HTTP I/O only — no business logic, no DB queries.
   - Services: Business logic, authorization checks, AI orchestration.
   - DB layer: Data access only — no business rules.

4. **Check existing reusable components.**
   - `core/config.py` — all configuration; never use `os.environ.get()` directly
   - `core/errors.py` — all error types; never raise bare `HTTPException` in services
   - `core/logging.py` — all logging; never use `print()` for application output
   - `core/security.py` — auth utilities; never implement JWT handling elsewhere
   - `core/middleware.py` — request ID middleware

5. **Avoid duplicate implementations.**
   - One service per domain. Do not create `user_service2.py`.
   - One model per entity. Do not create parallel model definitions.
   - One error code per error condition. Check `ErrorCode` enum before adding.

---

## While Coding

### Architecture Rules

- **Service layer is mandatory.** Business logic lives in `services/`, not in route handlers.
- **Schemas are separate from DB models.** API request/response shapes live in `schemas/`; database shapes live in `genesis_db/`.
- **Config module is the only config source.** Import `from core.config import settings`. Never call `os.environ.get()` directly in application code.
- **Use structured logging.** Import `from core.logging import get_logger`. Never use `print()` for application output.
- **Use canonical errors.** Raise `GenesisError` subclasses from service code. Check `ErrorCode` before adding new codes.
- **Versioned routes.** All new API routes go under `/api/v1/`. Do not add routes to the unversioned `/api/` prefix except for infrastructure endpoints (health, metrics).

### Database Rules

- **Migrations only.** Schema changes require an Alembic migration. Never use `create_db_and_tables()` in production code.
- **Explicit table names.** Every SQLModel table class must define `__tablename__`.
- **Timezone-aware timestamps.** Use `sa_column=Column(DateTime(timezone=True))` for all datetime fields.
- **`updated_at` must use `onupdate`.** Always include `onupdate=func.now()` on `updated_at` columns.
- **Index foreign keys.** Every `foreign_key=` field must also have `index=True`.
- **Name indexes explicitly.** Composite or non-trivial indexes must have explicit names.

### Security Rules

- **Never hardcode secrets.** No API keys, passwords, tokens, or credentials in source code.
- **Never add fallback secrets.** `os.environ.get("JWT_SECRET", "some-default")` is forbidden.
- **Validate all input.** Every API endpoint must use a Pydantic schema for request validation.
- **Restrict CORS.** Never set `allow_origins=["*"]`. Use `settings.cors_origins`.
- **Server-side authorization.** Never rely on client-provided user IDs for authorization — derive identity from the authenticated token.
- **Sanitize error messages.** Do not expose stack traces, SQL queries, or internal paths to clients in production.
- **No sensitive data in logs.** Passwords, tokens, API keys, and PII must never appear in log output.

### AI Governance Rules

Every AI-powered feature MUST:

1. **Register models** — use `model_registry` table; never hardcode model names.
2. **Register prompts** — use `prompt_registry` table; never embed system prompts inline in code.
3. **Register agents** — use `agent_registry` table; define `allowed_tools`, `risk_level`, `requires_approval`.
4. **Create AI run records** — every AI execution path must create an `ai_run` record before execution starts.
5. **Validate LLM output** — treat all LLM-generated structured data as untrusted; validate against schema before use.
6. **Respect risk levels** — never execute HIGH or CRITICAL risk actions without checking approval state.
7. **No user PII in AI run records** — store summaries and IDs, not full content.
8. **No inline prompt injection** — never interpolate raw user input into system prompts.

See `docs/AI_GOVERNANCE.md` for the complete governance specification.

### Type Safety

- All Python code must be fully type-annotated.
- All TypeScript code must be strictly typed (`"strict": true` in tsconfig).
- Do not use `Any` except where genuinely unavoidable, and document why.
- Run `mypy` / `pyright` before considering a task complete.

### Testing

- Every new service function must have at least one unit test.
- Every new API endpoint must have at least one integration test.
- AI agent behavior must have evaluation test cases.
- Tests live in `tests/` directories adjacent to the code they test.
- Do not mark tests as `xfail` to silence failures — fix the code.

---

## Before Completing a Task

Before declaring any task complete, you MUST run the following. If any check fails, fix it before completing.

### Python

```bash
# Format
uv run ruff format .

# Lint
uv run ruff check .

# Type check
uv run mypy apps/api/src packages/db

# Tests (when implemented)
uv run pytest
```

### TypeScript

```bash
# Format
pnpm format

# Lint
pnpm lint

# Type check
pnpm check-types
```

### Infrastructure

```bash
# Verify migrations are consistent
cd packages/db && DATABASE_URL=<test_url> alembic check

# Verify Docker compose is valid
docker compose -f infrastructure/docker/compose/docker-compose.yml config --quiet
```

### Security checklist

- [ ] No secrets or credentials in changed files
- [ ] No `allow_origins=["*"]` added
- [ ] No hardcoded model names outside `model_registry`
- [ ] No inline system prompts outside `prompt_registry`
- [ ] No `print()` used for application logging
- [ ] No business logic added directly to route handlers
- [ ] Environment variables documented in `.env.example`

### Documentation checklist

- [ ] ADR created if an architectural decision was made
- [ ] RFC created if a new subsystem or interface was designed
- [ ] `docs/infrastructure.md` updated if infrastructure changed
- [ ] `infrastructure/version.json` updated if infrastructure changed
- [ ] `docs/AI_GOVERNANCE.md` updated if new AI feature was added
- [ ] API schemas documented (FastAPI OpenAPI auto-docs are not sufficient for complex flows)

---

## What Agents MUST NOT Do

- **Rewrite working systems without justification.** Refactor only when there is a measurable benefit.
- **Introduce duplicate abstractions.** One service per domain, one model per entity, one error code per condition.
- **Bypass validation.** Never call DB directly from route handlers. Never use raw LLM output in business logic.
- **Hardcode secrets.** No exceptions.
- **Disable security controls.** Never set `allow_origins=["*"]`. Never remove authentication from protected routes.
- **Modify architecture without an ADR.** Framework changes, new infrastructure components, and layer boundary changes require documented decisions.
- **Add dependencies without justification.** Every new package dependency must be justified in the PR description.
- **Create undocumented APIs.** Every public API endpoint must be present in the OpenAPI schema.
- **Give agents unrestricted tool access.** `allowed_tools` must be a minimal explicit list.
- **Treat LLM output as trusted.** Always validate LLM-generated structured data against a Pydantic schema.
- **Delete existing implementations** without verifying they are unreferenced and replaced.
- **Commit directly to main.** All changes go through pull requests.

---

## Code Style Reference

### Python

```python
# Imports: standard library, then third-party, then local
import uuid
from datetime import datetime

from fastapi import Depends
from sqlmodel import Session

import genesis_db
from core.config import settings
from core.errors import NotFoundError, ErrorCode
from core.logging import get_logger

logger = get_logger(__name__)

# Functions: annotated, documented
def create_something(session: Session, user: genesis_db.User, name: str) -> genesis_db.Something:
    """
    Create a Something.
    
    Raises:
        ConflictError: if Something with this name already exists.
    """
    ...
```

### TypeScript

```typescript
// Always define explicit return types
async function fetchProject(id: string): Promise<Project> {
  ...
}

// Use const over let; let over var
const config = loadConfig();

// Avoid any — use unknown and narrow it
function processData(data: unknown): ProcessedData {
  if (!isValidData(data)) throw new Error("Invalid data shape");
  ...
}
```

---

## Repository Layout Reference

```
GENESIS_AI/
├── apps/
│   ├── api/                    FastAPI backend
│   │   └── src/
│   │       ├── api/v1/         Route handlers (thin — no business logic)
│   │       ├── core/           Config, errors, logging, middleware, security
│   │       ├── schemas/        API request/response schemas (separate from DB models)
│   │       └── services/       Business logic services
│   ├── web/                    Next.js frontend
│   ├── worker/                 NATS message consumer
│   └── dashboard/              Admin dashboard (future)
├── packages/
│   ├── db/                     Shared DB models (genesis_db) + Alembic migrations
│   │   └── genesis_db/
│   │       ├── models.py       Core entity models
│   │       ├── governance.py   AI governance models
│   │       └── database.py     Engine + session
│   ├── cli/                    Developer CLI (TypeScript)
│   └── ui/                     Shared React components
├── infrastructure/
│   └── docker/compose/         Docker Compose files (layered)
├── docs/
│   ├── adr/                    Architectural Decision Records
│   ├── rfc/                    Request for Comments
│   ├── architecture/           System overview documents
│   ├── AI_GOVERNANCE.md        AI governance specification
│   ├── PROJECT_AUDIT.md        Audit findings and priorities
│   ├── BACKEND_SCHEMA.md       Target database schema
│   └── process.md              Engineering process
└── scripts/                    Infrastructure lifecycle scripts
```

---

## Governance Pre-Merge Checklist (AI Features)

Before merging any PR that introduces AI functionality:

- [ ] Model registered in `model_registry`
- [ ] System prompt registered in `prompt_registry` (no inline prompts)
- [ ] Agent registered in `agent_registry` with explicit `allowed_tools` and `risk_level`
- [ ] `ai_run` records created in all AI execution paths
- [ ] LLM output validated against Pydantic schema before use in business logic
- [ ] Approval check implemented for HIGH/CRITICAL risk operations
- [ ] No user PII in `ai_run.input_summary` or `ai_run.output_summary`
- [ ] Evaluation test cases written and passing
- [ ] Failure paths tested (malformed output, tool failure, timeout)
- [ ] `docs/AI_GOVERNANCE.md` updated if new agent/tool/policy introduced
