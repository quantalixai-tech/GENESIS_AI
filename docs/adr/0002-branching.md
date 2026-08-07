# ADR 0002 — Branching Strategy

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-07 |
| **Phase** | 0.1 |
| **Deciders** | Genesis Core Team |

## Context

Genesis needs a branching strategy that:
1. Keeps `main` always deployable / always working
2. Enables parallel development on features without blocking each other
3. Supports the phase-based development roadmap (0.x, 1.x, 2.x)
4. Keeps the Git history clean and navigable
5. Is simple enough that developers don't need to think about it

## Decision

Use a **trunk-based development** model with short-lived feature branches and phase tags.

### Branch structure

```
main
  └── feature/phase-0.2-infra-bootstrap
  └── feature/phase-0.3-api-core
  └── fix/postgres-health-check
  └── docs/adr-0004-health
```

### Naming conventions

| Branch type | Pattern | Example |
|---|---|---|
| Phase work | `feature/phase-X.Y-<short-name>` | `feature/phase-0.2-infra-bootstrap` |
| Bug fixes | `fix/<short-description>` | `fix/nats-config-port` |
| Documentation | `docs/<short-description>` | `docs/infrastructure-contract` |
| Hotfixes | `hotfix/<short-description>` | `hotfix/env-missing-postgres` |

### Tags

Each completed phase is tagged:
```
v0.1.0  ← Phase 0.1 complete (Monorepo Bootstrap)
v0.2.0  ← Phase 0.2 complete (Infrastructure Bootstrap)
v0.3.0  ← Phase 0.3 complete (API Core)
```

### Commit message format

```
<type>(<scope>): <short description>

[optional body]
[optional footer]
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `ci`

Examples:
```
feat(infra): add docker compose for postgres, nats, minio
docs(adr): add ADR 0003 for tech stack decisions
fix(scripts): handle docker desktop socket on macos
chore(deps): update turbo to 2.10.8
```

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **Trunk-based + short-lived branches** | Clean history, fast CI, simple model | Requires discipline on branch lifetime |
| Gitflow (main + develop + feature + hotfix + release) | Formal release model | Heavyweight, complex for early-stage project |
| GitHub Flow (main + feature) | Simple | No clear release model |
| Feature flags on main | No merge conflicts | Requires feature flag infrastructure |

## Rationale

Gitflow is designed for teams shipping packaged software on fixed release schedules. Genesis is a platform that evolves continuously — the phase model already provides the release structure (v0.2.0, v0.3.0, etc.).

Trunk-based development keeps `main` healthy, reduces merge conflicts (short-lived branches), and aligns with how high-performing engineering teams (Google, Netflix, Etsy) work at scale.

The phase-scoped branch naming (`feature/phase-X.Y-name`) ties every branch to the roadmap, making it easy to understand what's in progress at a glance.

## Consequences

**What becomes easier:**
- `main` is always in a working state
- Phase progress is visible in branch names and tags
- Reviewing a phase's entire contribution is one `git log v0.1.0..v0.2.0`
- No long-lived feature branches rotting for weeks

**What becomes harder:**
- Developers must merge or rebase frequently (no "sit on a branch for 2 weeks")
- Large phases must be broken into small, mergeable increments

**New constraints introduced:**
- Branches older than 2 weeks without a PR are stale and should be deleted
- `main` must never be force-pushed
- Every phase completion must create a semver tag (`vX.Y.0`)

## References

- ADR 0001 — Monorepo Architecture
- [Trunk Based Development](https://trunkbaseddevelopment.com/)
- [Conventional Commits](https://www.conventionalcommits.org/)
