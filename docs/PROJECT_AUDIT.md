# PROJECT_AUDIT

**Document ID:** AUDIT-001
**Project:** AI-Driven Software Development Platform (GENESIS AI)
**Audit Date:** 2026-08-08
**Auditor:** Senior Staff Engineer / AI Systems Architect
**Repository Phase at Audit:** 0.3 (Core Platform Foundation partially complete)

---

# 1. Current Architecture

The repository is organized as a **polyglot monorepo** using pnpm workspaces (TypeScript) and uv workspaces (Python), coordinated by Turborepo.

```text
Monorepo Root
  ├── apps/
  │   ├── api/          Python / FastAPI — REST API + Auth
  │   ├── web/          TypeScript / Next.js — Frontend (stub)
  │   ├── worker/       Python / asyncio+NATS — Background worker (stub)
  │   └── dashboard/    Empty (.gitkeep only)
  ├── packages/
  │   ├── db/           Python — SQLModel models + Alembic migrations
  │   ├── cli/          TypeScript — CLI commands (stubs)
  │   ├── ui/           TypeScript — Shared UI components (Turborepo default)
  │   ├── config/       Empty
  │   ├── sdk/          Empty
  │   ├── shared/       Empty
  │   ├── types/        Empty
  │   ├── eslint-config/ ESLint shared config
  │   └── typescript-config/ TS shared config
  └── infrastructure/
      ├── docker/compose/ Docker Compose files (core + platform overlays)
      ├── postgres/     Postgres init.sql
      ├── nats/         NATS config
      ├── minio/        MinIO config
      └── version.json  Infrastructure manifest
```

**Current layer separation:**

```text
Next.js (web) — Default Turborepo template [not connected to API]
     ↓
FastAPI (api) — Routes contain business logic directly
     ↓
genesis_db (db package) — SQLModel models (User, Workspace, Project)
     ↓
PostgreSQL (via Docker)
```

**Background processing:**

```text
NATS → Worker (asyncio) → DB [basic subscriber, no real processing]
```

---

# 2. Repository Structure

| Directory | Purpose | Status |
|---|---|---|
| `apps/api/` | FastAPI backend — auth, workspaces, projects | Implemented (Phase 0.3) |
| `apps/web/` | Next.js frontend | Default Turborepo template — not customized |
| `apps/worker/` | NATS message consumer | Minimal stub |
| `apps/dashboard/` | Admin dashboard | Empty |
| `packages/db/` | Shared DB models + Alembic | Implemented (3 tables) |
| `packages/cli/` | Developer CLI tool | TypeScript stubs only |
| `packages/ui/` | Shared React components | Turborepo default |
| `packages/config/` | Configuration utilities | Empty directory |
| `packages/sdk/` | SDK for external consumers | Empty directory |
| `packages/shared/` | Shared utilities | Empty directory |
| `packages/types/` | Shared TypeScript types | Empty directory |
| `infrastructure/` | Docker, NATS, Postgres configs | Implemented |
| `docs/adr/` | Architectural Decision Records | 4 ADRs present |
| `docs/rfc/` | Request for Comments | 5 RFCs present |
| `docs/architecture/` | System architecture docs | 4 overview docs |
| `scripts/` | Shell scripts for infra lifecycle | Implemented |

---

# 3. Implementation Status

| Requirement | Current Status | Existing Implementation | Gap | Priority |
|---|---|---|---|---|
| Repository + monorepo structure | Complete | pnpm + uv + Turborepo | — | — |
| Local dev infrastructure (Docker) | Complete | Postgres/NATS/MinIO compose | — | — |
| User entity + authentication | Partial | JWT signup/login/me with HttpOnly cookies | No email validation, insecure fallback secret, 7-day hardcoded expiry | P0 |
| Workspace entity | Complete | CRUD routes + DB model | Not in BACKEND_SCHEMA.md (intentional extension) | Low |
| Project entity | Partial | Create/list/delete | Missing status, project_type fields from schema | P2 |
| Structured error handling | Missing | FastAPI defaults only | No error model, no error codes | P1 |
| Structured logging | Missing | `print()` in worker | No trace IDs, no structured format | P1 |
| Request IDs / trace IDs | Missing | Not implemented | Required for observability | P1 |
| Configuration management | Missing | `os.environ.get()` scattered | No settings module | P1 |
| Service layer | Missing | Business logic in routes | No separation of concerns | P1 |
| API versioning | Missing | `/api/...` (no v1 prefix) | Breaking change risk | P1 |
| Database migrations | Partial | Alembic + 1 migration | Only 3 tables vs 25+ in schema | P2 |
| Health check (real) | Incorrect | Returns hardcoded `"db": "connected"` | Does not test DB connection | P0 |
| CORS security | Incorrect | `allow_origins=["*"]` | Wildcard CORS | P0 |
| Rate limiting | Missing | Not implemented | Auth endpoints unprotected | P1 |
| Conversations model | Missing | Not implemented | Phase 2 requirement | P2 |
| Requirements model | Missing | Not implemented | Phase 2 requirement | P2 |
| AI agent framework | Missing | Not implemented | Phase 5 requirement | P2 |
| Agent registry | Missing | Not implemented | AI governance gap | P1 |
| Model registry | Missing | Not implemented | AI governance gap | P1 |
| Prompt registry | Missing | Not implemented | AI governance gap | P1 |
| Tool registry | Missing | Not implemented | AI governance gap | P1 |
| AI execution records | Missing | Not implemented | AI governance gap | P1 |
| Audit logging | Missing | Not implemented | AI governance + security gap | P1 |
| Human-in-the-loop | Missing | Not implemented | AI governance gap | P2 |
| Frontend application | Missing | Turborepo default template | No Genesis UI, no auth, no API connection | P2 |
| Live preview | Missing | Not implemented | Phase 7 requirement | P3 |
| Code generation | Missing | Not implemented | Phase 6 requirement | P3 |
| Validation engine | Missing | Not implemented | Phase 8 requirement | P3 |
| CLI tooling | Missing | TypeScript stubs only | Phase 11 requirement | P2 |
| Tests of any kind | Missing | Zero tests | Quality + process gap | P1 |
| CI/CD pipeline | Missing | No .github/ or CI config | Process gap | P2 |
| AI_GOVERNANCE.md | Missing | Not created | Governance doc gap | P1 |
| AGENTS.md | Missing | Not created | Engineering rules gap | P1 |

---

# 4. Architecture Issues

## ISSUE-001: No Service Layer
**Problem:** Route handlers directly execute business logic and database queries.
**Example:** `auth.py` creates users, hashes passwords, generates tokens — all in the route function.
**Why it matters:** Business logic is untestable, duplicated, and difficult to extend. Services cannot be reused across routes.

## ISSUE-002: DB Models Used as API Response Models
**Problem:** `genesis_db.UserPublic`, `genesis_db.ProjectPublic` are Pydantic views of SQLModel table classes, exposed directly as API response models.
**Why it matters:** Couples the API contract to the database schema. Any schema change breaks the API. Internal DB fields can accidentally leak.

## ISSUE-003: No Structured Error Model
**Problem:** Errors are raised as raw `HTTPException` with string `detail` messages.
**Why it matters:** Frontend and clients cannot reliably parse errors. Error codes are non-standardized. Debugging is difficult.

## ISSUE-004: No Configuration Module
**Problem:** Configuration is read via `os.environ.get("KEY", "default")` scattered across files.
**Why it matters:** No central place to validate required configuration. Missing required env vars fail silently with insecure defaults.

## ISSUE-005: API Versioning Absent
**Problem:** All routes are at `/api/...` with no version prefix.
**Why it matters:** Any breaking API change affects all existing clients immediately. No backward-compatible migration path.

## ISSUE-006: No Request Tracing
**Problem:** No request ID, trace ID, or correlation ID is generated or passed through the request lifecycle.
**Why it matters:** Impossible to correlate logs with requests, debug production issues, or trace AI agent executions.

## ISSUE-007: Worker Uses print() for Logging
**Problem:** All worker output is via `print()`.
**Why it matters:** No structured format, no levels, no context. Cannot be queried, filtered, or aggregated.

## ISSUE-008: Workspace Not in Schema
**Problem:** The `Workspace` entity (User → Workspace → Project hierarchy) is implemented but not present in `BACKEND_SCHEMA.md`, which specifies `projects.owner_id → users.id` directly.
**Decision:** Retaining `Workspace` as a valid project-grouping concept, documented as an intentional extension.

## ISSUE-009: updated_at Never Updated
**Problem:** `updated_at` fields are set at creation time and never updated subsequently. There is no `onupdate` handler.
**Why it matters:** Any query relying on `updated_at` for change detection will be incorrect.

---

# 5. Technical Debt

| Item | Location | Severity | Notes |
|---|---|---|---|
| `create_db_and_tables()` helper | `genesis_db/database.py` | High | Bypasses Alembic — confusing and dangerous |
| CLI commands are all stubs throwing `Error('Not implemented')` | `packages/cli/src/commands/` | Medium | Phase 0.3 target, expected debt |
| `packages/shared`, `packages/types`, `packages/sdk`, `packages/config` empty | `packages/` | Medium | Empty directories with no purpose yet |
| `apps/dashboard` empty | `apps/dashboard/` | Low | Placeholder only |
| `apps/web` is Turborepo default template | `apps/web/` | High | Not useful; confusing as-is |
| `TODO(phase-0.3)` comments throughout CLI | `packages/cli/` | Low | Expected |
| Health endpoint returns static string | `health.py` | High | Misleading in production |
| RFC 0001/0002/0003 are size-zero files | `docs/rfc/` | Medium | May be incomplete/placeholder |
| `infrastructure/version.json` incorrectly marks API/Worker as "planned" | `infrastructure/version.json` | Medium | Phase 0.3 complete |

---

# 6. Security Issues

## SEC-001 — Hardcoded JWT Secret Fallback (CRITICAL)
**Location:** `apps/api/src/core/security.py:11`, `infrastructure/docker/compose/docker-compose.platform.yml:12`
**Issue:** `SECRET_KEY = os.environ.get("JWT_SECRET", "supersecret-dev-key")` — application will start and accept tokens signed with this known key if `JWT_SECRET` is unset.
**Risk:** Any attacker can forge valid JWTs if this default is used in any deployment.
**Fix:** Raise startup error if `JWT_SECRET` is not set. Remove from compose fallback.

## SEC-002 — Wildcard CORS (HIGH)
**Location:** `apps/api/src/main.py:13`
**Issue:** `allow_origins=["*"]` allows any origin to make credentialed requests.
**Risk:** Cross-Site Request Forgery from any web page.
**Fix:** Restrict to configured list (default: `http://localhost:3000`).

## SEC-003 — No Input Validation Beyond Type Checking (MEDIUM)
**Location:** `apps/api/src/api/routes/auth.py`
**Issue:** Email field accepts any string (e.g., `"notanemail"`). Password accepts empty string.
**Fix:** Add Pydantic validators for email format (using `pydantic[email]`) and password minimum length.

## SEC-004 — False Health Endpoint (MEDIUM)
**Location:** `apps/api/src/api/routes/health.py`
**Issue:** Returns `"db": "connected"` without testing DB connectivity. Load balancers/monitors will believe the service is healthy when the DB is down.
**Fix:** Perform an actual DB probe (e.g., `SELECT 1`).

## SEC-005 — JWT_SECRET Missing from .env.example (MEDIUM)
**Location:** `.env.example`, `.env.development`
**Issue:** `JWT_SECRET` is required by `docker-compose.platform.yml` but not documented in `.env.example`.
**Fix:** Add to both files with a clear warning.

## SEC-006 — No Rate Limiting on Auth Endpoints (MEDIUM)
**Location:** `/api/auth/login`, `/api/auth/signup`
**Issue:** No protection against brute-force login attempts.
**Fix:** Document as known gap; add to `AI_GOVERNANCE.md` and `AGENTS.md` as a P1 requirement.

## SEC-007 — AI-Specific Risks (Future)
The following AI-specific security mechanisms are not yet implemented and must be addressed before AI agent features are built:
- Prompt injection controls
- LLM output validation before use in business logic
- Tool permission boundaries
- Agent execution sandboxing
- Context poisoning prevention

---

# 7. AI Governance Gaps

The following governance mechanisms are completely absent:

| Mechanism | Status | Required By |
|---|---|---|
| Model Registry | Missing | Phase 5+ (agent orchestration) |
| Prompt Registry | Missing | Phase 5+ |
| Agent Registry | Missing | Phase 5+ |
| Tool Registry | Missing | Phase 5+ |
| Policy Registry | Missing | Phase 5+ |
| AI Run / Execution Records | Missing | Phase 5+ |
| Human Approval Mechanism | Missing | Phase 5+ |
| AI Audit Log | Missing | Phase 5+ |
| Evaluation Registry | Missing | Phase 5+ |
| Observability (AI-specific) | Missing | Phase 5+ |

**Governance database tables to introduce now (foundation only):**
- `agent_registry` — defines agents, their capabilities, allowed tools, risk level
- `model_registry` — defines models, versions, providers
- `prompt_registry` — defines prompts, versions, associated model constraints
- `ai_run` — execution record for every AI operation

These are lightweight registry tables that should be established before AI agent code is written, so that governance is baked in from the start rather than retrofitted.

---

# 8. Recommended Refactoring

## P0 — Must fix before further development

1. **SEC-001** — Remove hardcoded JWT secret fallback; require explicit env var
2. **SEC-002** — Restrict CORS to configured origins
3. **SEC-004** — Fix health endpoint to perform real DB check
4. **SEC-005** — Add `JWT_SECRET` and `DATABASE_URL` to `.env.example`

## P1 — Fix during foundation refactor (this session)

5. **ISSUE-004** — Create centralized config module (pydantic-settings)
6. **ISSUE-001** — Introduce service layer
7. **ISSUE-002** — Separate API schemas from DB models
8. **ISSUE-003** — Create structured error model
9. **ISSUE-006** — Add request ID middleware and structured logging
10. **ISSUE-005** — Add API versioning (`/api/v1/`)
11. **ISSUE-009** — Fix `updated_at` to auto-update
12. **DEBT-001** — Remove `create_db_and_tables()` helper
13. **GOV-001** — Create AI governance DB tables (foundation)
14. Create `docs/AI_GOVERNANCE.md`
15. Create `AGENTS.md`

## P2 — Address during subsequent development

16. Add tests (unit, integration, API)
17. Add CI/CD pipeline
18. Expand DB schema toward BACKEND_SCHEMA.md (conversations, requirements, etc.)
19. Replace Next.js default template with Genesis application shell
20. Implement CLI commands
21. Add rate limiting to auth endpoints
22. Implement `apps/dashboard`

## P3 — Future work

23. AI agent framework implementation (Phase 5)
24. Code generation pipeline (Phase 6)
25. Live preview (Phase 7)
26. Validation engine (Phase 8)
27. AI repair system (Phase 9)

---

# END OF PROJECT AUDIT
