# Infrastructure Contract

> **Version:** 0.1.0 | **Phase:** 0.2 | **Status:** Active

This document is the authoritative reference for Genesis infrastructure.
Every service, port, volume, and network is documented here.
When infrastructure changes, this document must be updated in the same PR.

---

## Services

| Service | Container | Image | Layer | Purpose |
|---|---|---|---|---|
| PostgreSQL | `genesis-postgres` | `postgres:16-alpine` | Core | Primary relational database |
| NATS | `genesis-nats` | `nats:2.10-alpine` | Core | Event bus / message broker |
| MinIO | `genesis-minio` | `minio/minio:latest` | Core | S3-compatible object storage |

### Future Services (not yet active)

| Service | Layer | Phase |
|---|---|---|
| API | Platform | 0.3 |
| Worker | Platform | 0.3 |
| Web | Platform | 0.4 |
| Dashboard | Platform | 0.4 |
| Ollama | AI | 1.0 |
| Model Router | AI | 1.0 |
| Prometheus | Observability | 1.0 |
| Grafana | Observability | 1.0 |
| Loki | Observability | 1.0 |

---

## Ports

| Service | Port | Protocol | Purpose |
|---|---|---|---|
| PostgreSQL | `5432` | TCP | Database client connections |
| NATS | `4222` | TCP | NATS client connections |
| NATS Monitoring | `8222` | HTTP | Health check endpoint, metrics |
| MinIO API | `9000` | HTTP/S3 | S3-compatible API |
| MinIO Console | `9001` | HTTP | Web management console |

> All ports are configurable via environment variables. See [Environment Variables](#environment-variables).

---

## Volumes

| Volume Name | Service | Mount Path | Purpose |
|---|---|---|---|
| `postgres-data` | PostgreSQL | `/var/lib/postgresql/data` | Database files |
| `nats-data` | NATS | `/data` | JetStream stream storage |
| `minio-data` | MinIO | `/data` | Object storage buckets |

**Volume strategy:** Named Docker volumes are used exclusively. Never bind-mount data directories to the host filesystem in production. This ensures data survives container restarts and updates.

---

## Networks

| Network | Driver | Purpose |
|---|---|---|
| `genesis-network` | `bridge` | All Genesis containers communicate on this network |

Every container added to the platform **must** join `genesis-network`. This ensures services can reference each other by container name (e.g., `postgres`, `nats`, `minio`) without hardcoding IP addresses.

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `POSTGRES_DB` | `genesis` | Database name |
| `POSTGRES_USER` | `genesis` | Database user |
| `POSTGRES_PASSWORD` | `genesis` | Database password — **change in production** |
| `POSTGRES_PORT` | `5432` | Host port mapping |
| `POSTGRES_HOST` | `postgres` | Service hostname (within Docker network) |
| `NATS_PORT` | `4222` | NATS client port |
| `NATS_MONITORING_PORT` | `8222` | NATS monitoring port |
| `NATS_HOST` | `nats` | Service hostname |
| `MINIO_ROOT_USER` | `minio` | MinIO root user — **change in production** |
| `MINIO_ROOT_PASSWORD` | `minio123` | MinIO root password — **change in production** |
| `MINIO_PORT` | `9000` | MinIO API port |
| `MINIO_CONSOLE_PORT` | `9001` | MinIO console port |
| `MINIO_HOST` | `minio` | Service hostname |
| `GENESIS_ENV` | `development` | Platform environment |
| `GENESIS_LOG_LEVEL` | `info` | Log verbosity |

---

## Health Checks

Each service exposes a health check. Docker uses these to determine readiness.

| Service | Health Check Command | Interval | Retries |
|---|---|---|---|
| PostgreSQL | `pg_isready -U $POSTGRES_USER -d $POSTGRES_DB` | 10s | 5 |
| NATS | `wget -qO- http://localhost:8222/healthz \| grep ok` | 10s | 5 |
| MinIO | `curl -f http://localhost:9000/minio/health/live` | 15s | 5 |

Health check status is visible via:
```bash
docker compose -f infrastructure/docker/compose/docker-compose.yml ps
```

---

## Running the Infrastructure

### First time

```bash
bash scripts/setup.sh
bash scripts/up.sh
```

### Daily use

```bash
bash scripts/up.sh       # start
bash scripts/down.sh     # stop (data preserved)
bash scripts/restart.sh  # restart
```

### Nuclear option

```bash
bash scripts/clean.sh    # stop + remove all volumes (destructive)
```

---

## Dependencies

```
PostgreSQL
  ← Projects, Users, Workspaces, Snapshots
  ← All relational data

NATS
  ← Event bus: ProjectCreated, WorkspaceOpened, UserLoggedIn
  ← Future: AI workflow orchestration events

MinIO
  ← Artifact storage: project files, snapshots, exports
  ← Future: model weights cache, generated outputs
```

---

## Compose File Structure

```
infrastructure/
└── docker/
    └── compose/
        ├── docker-compose.yml           ← Core services (this phase)
        ├── docker-compose.override.yml  ← Future layer stubs (commented)
        ├── docker-compose.ai.yml        ← AI services (Phase 1.0)
        ├── docker-compose.platform.yml  ← API, Worker, Web (Phase 0.3)
        └── docker-compose.observability.yml ← Prometheus, Grafana (Phase 1.0)
```

---

## Labels

Every container is labeled with:

| Label | Example Value | Purpose |
|---|---|---|
| `genesis.service` | `postgres` | Service name |
| `genesis.layer` | `core` | Architecture layer |
| `genesis.version` | `0.1.0` | Infrastructure version |

Labels enable tooling (CLI, dashboard) to discover and categorize containers automatically.

---

## Extending the Infrastructure

When adding a new service:

1. Add it to the appropriate `docker-compose.<layer>.yml` file
2. Join `genesis-network`
3. Add a health check
4. Add labels (`genesis.service`, `genesis.layer`, `genesis.version`)
5. Use named volumes for persistent data
6. Add environment variables to `.env.example`
7. Update this document
8. Update `infrastructure/version.json`
