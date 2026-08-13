# ADR-009 — Project Git Model

| Field | Value |
|---|---|
| **ADR Number** | 0009 |
| **Title** | Per-Project Git Repository Model |
| **Status** | Accepted |
| **Date** | 2026-08-13 |
| **Phase** | 1.0 |

---

## Context

Each project needs its own version-controlled file system so that:
1. Every AI-generated change is traceable to the requirement/task that caused it
2. Users can restore previous working states
3. The diff between changes is inspectable

Options considered:
1. **Host filesystem + gitpython** — bare git repos stored on the Docker volume; managed via `gitpython` Python library
2. **MinIO tarball snapshots** — project state stored as tarballs in MinIO; no real git
3. **libgit2 (pygit2)** — lower-level git library with more control
4. **Dulwich** — pure-Python git implementation, no C dependency

## Decision

**Host filesystem with `gitpython`** — each project gets a directory on the worker's shared volume; git repos are initialized with `git init` and managed via the `gitpython` library.

```
Filesystem layout:
  /projects/<project_id>/           ← project working directory
    .git/                           ← standard git repo
    frontend/                       ← generated frontend code
    backend/                        ← generated backend code
    ...
```

The `project.repository_path` field stores the absolute path. The API and worker share this volume (`genesis-projects` named Docker volume).

Commit metadata:
```
genesis(agent): generate authentication module

Task: TASK-001
Requirement: REQ-003
Agent: backend_agent
Run: <ai_run.id>
```

Git history is mirrored to `git_commits` DB table for fast querying without filesystem access.

## Rationale

- **gitpython**: Most mature Python git library; avoids shell injection (no subprocess); well-documented; supports all required operations (init, add, commit, diff, checkout, log)
- **Host filesystem**: Simple, debuggable, works with existing volume mounts; no encoding overhead
- **Not MinIO tarballs**: Not a real git history; can't diff incrementally; no branch support for future
- **Not pygit2/libgit2**: More complex C extension dependency; gitpython is sufficient for V1
- **Not Dulwich**: Less maintained; gitpython has better docs and community

## Consequences

- Add `gitpython` to `apps/api/pyproject.toml` and `apps/worker/pyproject.toml`
- Add named Docker volume `genesis-projects`, mounted at `/projects` in both API and worker containers
- `git_service.py` uses `gitpython` — no `subprocess` git calls
- Each commit writes a record to `git_commits` table with task/requirement traceability
- MinIO used for periodic backup of project archives (future phase — not V1)
- Worker container and API container must mount the same `genesis-projects` volume
