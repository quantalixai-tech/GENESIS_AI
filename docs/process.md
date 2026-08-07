# Genesis Engineering Process

> **Version:** 1.0 | **Status:** Active | **Applies to:** All phases

This document defines the standard engineering process for every phase of Genesis development.
Every phase must follow this pattern. No exceptions.

---

## The Pattern

```
ADR  →  RFC  →  Implementation Plan  →  Code  →  Acceptance Criteria  →  Verification
```

This is how large engineering organizations build systems.
It keeps Genesis consistent, auditable, and maintainable as it grows.

---

## Stage 1 — ADR (Architectural Decision Record)

**Document:** `docs/adr/XXXX-<name>.md`

**Purpose:** Record *why* an architectural decision was made.

An ADR answers:
- What problem are we solving?
- What options did we consider?
- What did we choose and why?
- What are the consequences?

ADRs are **permanent records**. Once merged, they are never deleted — only superseded by a new ADR that references the old one.

**Template:**

```markdown
# ADR XXXX — [Title]

| Field | Value |
|---|---|
| **Status** | Proposed / Accepted / Superseded |
| **Date** | YYYY-MM-DD |
| **Deciders** | [names] |

## Context
What is the problem or situation requiring a decision?

## Decision
What was decided?

## Options Considered
| Option | Pros | Cons |
|---|---|---|

## Rationale
Why did we choose this option over the others?

## Consequences
What becomes easier? What becomes harder? What new problems arise?

## References
Links to relevant RFCs, PRs, or external resources.
```

---

## Stage 2 — RFC (Request for Comments)

**Document:** `docs/rfc/XXXX-<name>.md`

**Purpose:** Define the *technical specification* before writing any code.

An RFC answers:
- What exactly are we building?
- What are the interfaces, data shapes, and contracts?
- What are the edge cases?
- How does this fit into the existing architecture?

RFCs are written before implementation begins. If implementation reveals the RFC was wrong, update the RFC before updating the code.

**Template:**

```markdown
# RFC XXXX — [Title]

| Field | Value |
|---|---|
| **RFC Number** | XXXX |
| **Status** | Draft / Accepted / Implemented |
| **Created** | YYYY-MM-DD |
| **Phase** | X.Y |

## Summary
One paragraph description.

## Motivation
Why are we doing this? What problem does it solve?

## Specification
The detailed technical design. Interfaces, schemas, protocols, etc.

## Alternatives Considered
What else could we have done?

## Implementation Plan
High-level breakdown of what needs to be built, in what order.

## Acceptance Criteria
How do we know this RFC is fully implemented?

## References
ADRs, external documentation, prior art.
```

---

## Stage 3 — Implementation Plan

**Purpose:** Break the RFC into concrete files to create, modify, or delete.

The implementation plan answers:
- Exactly which files change?
- In what order do we make changes?
- What are the dependencies between changes?

The implementation plan lives in the conversation context (not committed to the repo). Once execution begins, it is tracked via `task.md`.

---

## Stage 4 — Code

Write the code. Follow the implementation plan.

**Rules:**
- One PR per phase or sub-phase
- Every PR references its ADR and RFC
- No code without a health check / test plan
- Update `infrastructure/version.json` when infrastructure changes
- Update `docs/infrastructure.md` when infrastructure changes

---

## Stage 5 — Acceptance Criteria

**Defined in:** The RFC or implementation plan.

Acceptance criteria are binary: pass or fail.
They define what "done" means for this phase.

Example format:
```
✓ Docker Compose starts successfully
✓ PostgreSQL running and healthy
✓ NATS running and healthy
✓ MinIO running and healthy
✓ Persistent volumes survive container restart
✓ genesis-network created
✓ Environment variables loaded correctly
✓ Health checks pass (all services report healthy)
✓ Shell scripts are executable and work correctly
✓ Infrastructure documented in docs/infrastructure.md
```

---

## Stage 6 — Verification

**Purpose:** Prove that acceptance criteria are met.

Verification has two layers:

### Automated Verification
Commands that can be run in CI:
```bash
# Example for Phase 0.2
docker compose -f infrastructure/docker/compose/docker-compose.yml up -d
docker compose -f infrastructure/docker/compose/docker-compose.yml ps
# Assert all services show "healthy"
docker compose -f infrastructure/docker/compose/docker-compose.yml down
```

### Manual Verification
Steps a human performs to confirm the experience is correct.
Example: "Open localhost:9001, log in with minio/minio123, confirm the console loads."

---

## Document Numbering

| Type | Path | Format |
|---|---|---|
| ADR | `docs/adr/` | `XXXX-kebab-case-title.md` (e.g., `0001-monorepo.md`) |
| RFC | `docs/rfc/` | `XXXX-kebab-case-title.md` (e.g., `0004-health.md`) |

Numbers are sequential and never reused. Gap is okay (e.g., skip from 0003 to 0005 if 0004 was withdrawn).

---

## Phase Naming Convention

| Format | Meaning |
|---|---|
| Phase 0.x | Foundation — infrastructure, platform bootstrap, core APIs |
| Phase 1.x | AI Integration — models, inference, agents |
| Phase 2.x | Advanced Features — plugins, marketplace, collaboration |
| Phase 3.x | Scale — multi-tenant, distributed, cloud deployment |

---

## The Golden Rule

> **If a developer needs to read a 20-page setup guide, we've failed.**

Every phase should leave the platform in a state where:
1. A new developer can clone the repo
2. Run `genesis setup && genesis up`
3. Have a working environment

If that's not true at the end of a phase, the phase is not done.
