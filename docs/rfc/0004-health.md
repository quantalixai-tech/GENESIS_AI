# RFC 0004 — Health Check Specification

| Field | Value |
|---|---|
| **RFC Number** | 0004 |
| **Title** | Health Check Specification |
| **Status** | Draft |
| **Created** | 2026-08-07 |
| **Phase** | 0.2 |
| **Implements** | `genesis doctor` |

---

## Summary

This RFC defines the health check system for Genesis.
It specifies what is checked, in what order, how results are reported,
and what exit codes mean. This becomes the blueprint for `genesis doctor`.

---

## Motivation

A platform that can't tell you if it's healthy is a platform you can't trust.

Developers should be able to run a single command and know within seconds whether the platform is ready to use. The health check system must be:

- **Fast** — complete in under 5 seconds for required checks
- **Honest** — never report healthy when something is broken
- **Actionable** — every failure includes a remediation hint
- **Layered** — distinguish required from optional checks

---

## Health Check Hierarchy

Checks are executed in dependency order. If a foundational check fails,
dependent checks are skipped rather than reporting misleading failures.

```
Docker
  └─ Required: must pass before any service checks run
  
PostgreSQL
  └─ Required: data layer — nothing works without it
  
NATS
  └─ Required: event bus — all async workflows depend on it
  
MinIO
  └─ Required: artifact storage
  
Disk Space
  └─ Required: < 1 GB available triggers a warning; < 100 MB is an error
  
Ports
  └─ Required: all required ports must be available (or in use by Genesis)

GPU
  └─ Optional: not available → CPU mode only (warning, not error)
  
Models
  └─ Optional: if no models configured → warn, but don't fail
```

---

## Individual Check Specifications

### 1. Docker

| Property | Value |
|---|---|
| **Required** | Yes |
| **Description** | Docker daemon is installed and running |
| **Check method** | `docker info` exit code = 0 |
| **Pass** | Docker is running |
| **Fail** | Docker is not installed, or daemon is stopped |
| **On fail** | Skip all subsequent checks |
| **Remediation** | Install Docker Desktop: https://www.docker.com/products/docker-desktop |

---

### 2. PostgreSQL

| Property | Value |
|---|---|
| **Required** | Yes |
| **Description** | PostgreSQL container is running and accepting connections |
| **Check method** | TCP connect to `localhost:$POSTGRES_PORT` + `pg_isready` query |
| **Pass** | `pg_isready` returns 0 |
| **Fail** | Cannot connect, or container is unhealthy |
| **Remediation** | Run `bash scripts/up.sh` or check `docker logs genesis-postgres` |

---

### 3. NATS

| Property | Value |
|---|---|
| **Required** | Yes |
| **Description** | NATS server is running and JetStream is enabled |
| **Check method** | HTTP GET `http://localhost:$NATS_MONITORING_PORT/healthz` → `{"status":"ok"}` |
| **Pass** | Response contains `"ok"` |
| **Fail** | Request fails or returns non-ok status |
| **Remediation** | Run `bash scripts/up.sh` or check `docker logs genesis-nats` |

---

### 4. MinIO

| Property | Value |
|---|---|
| **Required** | Yes |
| **Description** | MinIO object storage is running and accepting requests |
| **Check method** | HTTP GET `http://localhost:$MINIO_PORT/minio/health/live` → 200 |
| **Pass** | HTTP 200 |
| **Fail** | Request fails or returns non-200 |
| **Remediation** | Run `bash scripts/up.sh` or check `docker logs genesis-minio` |

---

### 5. Disk Space

| Property | Value |
|---|---|
| **Required** | Yes (warn/error threshold) |
| **Description** | Sufficient disk space is available |
| **Check method** | `df -b /` — check available bytes |
| **Pass** | > 5 GB available |
| **Warn** | 1 GB – 5 GB available |
| **Error** | < 1 GB available |
| **Remediation** | Free up disk space or expand storage |

---

### 6. Ports

| Property | Value |
|---|---|
| **Required** | Yes |
| **Description** | All required ports are available or in use by Genesis |
| **Check method** | TCP connect attempt to each port; if port is open, verify it's a Genesis container |
| **Required Ports** | 5432, 4222, 8222, 9000, 9001 |
| **Pass** | All ports are free, or occupied by Genesis containers |
| **Fail** | A port is occupied by a non-Genesis process |
| **Remediation** | Stop the conflicting service or change Genesis port in `.env` |

---

### 7. GPU (Optional)

| Property | Value |
|---|---|
| **Required** | No |
| **Description** | NVIDIA GPU is available for AI acceleration |
| **Check method** | `nvidia-smi` exit code = 0, or `system_profiler SPDisplaysDataType` on macOS |
| **Pass** | GPU detected |
| **Skip** | No GPU detected — platform runs in CPU mode |
| **Note** | CPU mode is fully supported; GPU unlocks faster inference |

---

### 8. Models (Optional)

| Property | Value |
|---|---|
| **Required** | No |
| **Description** | At least one AI model is available for inference |
| **Check method** | Query Ollama API: `GET /api/tags` (Phase 1.0+) |
| **Pass** | One or more models are downloaded |
| **Skip** | Ollama not running (Phase 0.x — AI services not yet active) |
| **Note** | In Phase 0.x, this check is always skipped |

---

## Output Format

```
╔══════════════════════════════╗
║  Genesis — Health Report     ║
╚══════════════════════════════╝

▶ System

  ✓ Docker          — running (version 27.4.0)
  ✓ Disk            — 127 GB available
  ✓ Ports           — all required ports available

▶ Core Infrastructure

  ✓ PostgreSQL      — healthy (localhost:5432)
  ✓ NATS            — healthy (localhost:4222, JetStream enabled)
  ✓ MinIO           — healthy (localhost:9000)

▶ AI Services

  ○ GPU             — not available (CPU mode)
  ○ Models          — skipped (AI services not active)

──────────────────────────────

  Status: All systems healthy ✓
  Duration: 1.2s

```

### Status symbols

| Symbol | Meaning |
|---|---|
| `✓` | Healthy / Pass |
| `✗` | Unhealthy / Fail |
| `⚠` | Warning (degraded, not failed) |
| `○` | Skipped (optional, not applicable) |

---

## Exit Codes

| Code | Meaning |
|---|---|
| `0` | All required checks passed |
| `1` | One or more required checks failed |
| `2` | Invalid configuration (bad .env, missing compose file) |

---

## JSON Output Mode

For machine consumption (CI/CD pipelines, Dashboard):

```bash
genesis doctor --json
```

Output:
```json
{
  "overall": "healthy",
  "timestamp": "2026-08-07T09:00:00.000Z",
  "duration": 1234,
  "checks": [
    {
      "name": "docker",
      "status": "healthy",
      "required": true,
      "message": "Running version 27.4.0"
    },
    {
      "name": "postgres",
      "status": "healthy",
      "required": true,
      "message": "Accepting connections on localhost:5432"
    },
    {
      "name": "nats",
      "status": "healthy",
      "required": true,
      "message": "JetStream enabled, localhost:4222"
    },
    {
      "name": "minio",
      "status": "healthy",
      "required": true,
      "message": "Accepting requests on localhost:9000"
    },
    {
      "name": "disk",
      "status": "healthy",
      "required": true,
      "message": "127 GB available"
    },
    {
      "name": "ports",
      "status": "healthy",
      "required": true,
      "message": "All required ports available"
    },
    {
      "name": "gpu",
      "status": "skipped",
      "required": false,
      "message": "No GPU detected — CPU mode"
    },
    {
      "name": "models",
      "status": "skipped",
      "required": false,
      "message": "AI services not active (Phase 0.x)"
    }
  ]
}
```

---

## Implementation Plan

This RFC is implemented in phases:

| Phase | What gets implemented |
|---|---|
| 0.2 | This spec (the RFC itself) |
| 0.3 | `genesis doctor` CLI command — Docker, Ports, Disk checks |
| 0.3 | PostgreSQL, NATS, MinIO health checks |
| 1.0 | GPU detection |
| 1.0 | Model availability check |

---

## References

- [Infrastructure Contract](../infrastructure.md)
- [ADR 0003 — Tech Stack](../adr/0003-tech-stack.md)
- Docker health check documentation: https://docs.docker.com/engine/reference/builder/#healthcheck
- NATS monitoring: https://docs.nats.io/running-a-nats-service/nats_admin/monitoring
- MinIO health check: https://min.io/docs/minio/linux/operations/monitoring/healthcheck-probe.html
