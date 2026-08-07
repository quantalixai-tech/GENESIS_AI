# ADR 0001 — Monorepo Architecture

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-07 |
| **Phase** | 0.1 |
| **Deciders** | Genesis Core Team |

## Context

Genesis will ultimately consist of many components:
- Multiple applications (web, API, worker, dashboard, CLI)
- Multiple shared packages (ui, sdk, types, config, shared utilities)
- Infrastructure definitions and configuration
- Documentation

We need a repository strategy that:
1. Enables code sharing between components without publishing to npm
2. Enables consistent tooling (lint, format, type checking) across all packages
3. Supports incremental builds — only rebuild what changed
4. Keeps a single source of truth for dependencies and versioning
5. Doesn't require a complex monorepo management tool to get started

## Decision

Use a **pnpm workspace monorepo** managed by **Turborepo**.

Structure:
```
genesis/
├── apps/        ← Deployed applications (web, api, worker, dashboard)
├── packages/    ← Shared libraries (ui, sdk, cli, types, config, shared)
├── infrastructure/ ← Docker, configs, service definitions
├── docs/        ← Architecture decisions, RFCs, specifications
└── scripts/     ← Developer workflow automation
```

## Options Considered

| Option | Pros | Cons |
|---|---|---|
| **pnpm + Turborepo** | Fast, incremental, great DX, workspace linking, low overhead | |
| Nx | Feature-rich, code generation | Complex configuration, heavy |
| Lerna | Established | Largely superseded by Turborepo; slower |
| Multiple repos (polyrepo) | Team autonomy per repo | No code sharing, version drift, complex CI |
| Yarn workspaces | Widely used | pnpm is faster, more disk-efficient |

## Rationale

**pnpm** uses a content-addressable store and hard links — dramatically faster installs and less disk usage than npm or yarn. Workspace protocol (`workspace:*`) makes internal package linking explicit and reliable.

**Turborepo** adds:
- Incremental builds (only rebuild affected packages)
- Remote caching (share build artifacts across machines — relevant for CI)
- Pipeline definition (declare what depends on what)
- Zero framework lock-in

The combination is the current industry standard for TypeScript monorepos (used by Vercel, Linear, Shadcn, and others).

## Consequences

**What becomes easier:**
- `@genesis/types` imported by `@genesis/api`, `@genesis/web`, and `@genesis/cli` with zero publish step
- `turbo run build` only rebuilds changed packages
- Single `prettier` and `eslint` config applied everywhere
- One `pnpm install` installs all dependencies for all packages

**What becomes harder:**
- Developers unfamiliar with monorepos need a brief orientation
- `package.json` `name` fields must be unique across all packages

**New constraints introduced:**
- All packages under `packages/` must be named `@genesis/<name>`
- All apps under `apps/` must be named `@genesis/<name>-app` or similar
- `pnpm-workspace.yaml` must be updated when adding new package locations

## References

- [Turborepo documentation](https://turbo.build/repo/docs)
- [pnpm workspaces](https://pnpm.io/workspaces)
- ADR 0002 — Branching Strategy
