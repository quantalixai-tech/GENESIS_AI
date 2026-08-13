# ADR-007 — Sandbox Execution Architecture

| Field | Value |
|---|---|
| **ADR Number** | 0007 |
| **Title** | Sandbox Execution Architecture |
| **Status** | Accepted |
| **Date** | 2026-08-13 |
| **Phase** | 1.0 |

---

## Context

Generated code must be built, tested, and previewed in an isolated environment. Running generated code in the API or worker process would be a critical security risk.

Options considered:
1. **Docker SDK per project** — each project gets an isolated Docker container for build/test/preview; managed via Docker Python SDK
2. **gVisor (runsc)** — kernel-level sandbox for Docker containers
3. **Subprocess with resource limits** — run build commands in subprocesses with ulimits
4. **WebAssembly (WASM)** — compile and run generated code in a WASM sandbox

## Decision

**Docker SDK (per-project containers)** for build/test/preview execution, managed from the worker process.

Each project maintains a named container (`genesis-sandbox-<project_id>`) with:
- Project files mounted from a named Docker volume
- Resource limits: 1 CPU, 512MB RAM (configurable via agent_registry)
- No outbound network except npm/pip registries (allowlisted)
- Execution timeout: from `agent_registry.max_execution_seconds`

Worker sandbox handler:
```
WorkerSandboxHandler
  → docker.containers.run(...)
  → captures stdout/stderr
  → returns exit_code + output to NATS reply subject
  → publishes to validation_run record
```

## Rationale

- **Docker isolation**: Complete filesystem and network isolation without kernel-level complexity
- **Docker Python SDK**: `docker` package is well-maintained and avoids shell injection risks
- **Per-project containers**: Simple mapping; container name derived from project ID
- **gVisor not selected**: Adds operational complexity; Docker-level isolation is sufficient for V1
- **WASM not selected**: Too early to support the full range of generated project types

## Consequences

- Worker requires Docker socket access (security implication: documented and intentional)
- Container startup adds ~2-3s to first build — acceptable for V1
- Container images must be pre-built for common stacks (Node.js, Python, etc.)
- Volume mount strategy: project files on named volume, shared between API and worker
- Add `docker` Python package to worker dependencies
- Maximum sandbox lifetime: 10 minutes; containers auto-removed after execution
