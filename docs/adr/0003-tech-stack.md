# ADR 0003 — Core Infrastructure Technology Stack

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-07 |
| **Phase** | 0.2 |
| **Deciders** | Genesis Core Team |

## Context

Genesis needs a persistent data store, an event bus, and an artifact storage system.
These are the foundational services that every other component will depend on.

The choices made here are difficult and costly to reverse — they define the data model capabilities, the event system semantics, and the artifact management approach for the entire platform's lifetime.

## Decision

**PostgreSQL** as the primary relational database.
**NATS (with JetStream)** as the event bus and message broker.
**MinIO** as the S3-compatible object storage system.

## Options Considered

### Database

| Option | Pros | Cons |
|---|---|---|
| **PostgreSQL** | Battle-tested, rich extensions (uuid-ossp, pgcrypto, pgvector), excellent tooling, ACID compliance, JSON support | Requires schema migrations |
| SQLite | Zero-ops, simple | Not suitable for multi-service access, no horizontal scaling |
| MongoDB | Flexible schema | Weaker consistency guarantees, less suitable for relational project/user data |
| MySQL/MariaDB | Widely used | Inferior extension ecosystem, weaker JSON support |

### Event Bus

| Option | Pros | Cons |
|---|---|---|
| **NATS + JetStream** | Lightweight, high-performance, persistent streams, exactly-once delivery, simple config | Smaller community than Kafka |
| Kafka | Industry standard, extremely high throughput | Heavy operationally, complex setup, excessive for Phase 0 |
| Redis Streams | Simple, fast | Limited stream semantics, not a dedicated message broker |
| RabbitMQ | Mature, feature-rich | Complex routing model, heavier than NATS |

### Object Storage

| Option | Pros | Cons |
|---|---|---|
| **MinIO** | S3-compatible (zero migration to AWS S3), excellent SDK support, self-hosted | Requires separate deployment |
| Local filesystem | Simplest | Not scalable, no multi-service access, no built-in replication |
| AWS S3 | Industry standard | Cloud dependency, costs money, not self-hosted |

## Rationale

### PostgreSQL
The project/workspace/user data model is inherently relational. PostgreSQL's extension ecosystem (`pgvector` for future embeddings, `uuid-ossp` for UUID primary keys, `pgcrypto` for secure token storage) makes it uniquely suited to an AI platform. No other database matches this combination.

### NATS + JetStream
Genesis will evolve into an event-driven system where AI agents, workflows, and UI components communicate asynchronously. NATS JetStream provides persistent streams (survives restarts), message replay (new consumers can catch up), and exactly-once delivery semantics — all at a fraction of Kafka's operational complexity. It starts as a lightweight event bus in Phase 0 and scales to handle complex AI workflow orchestration in Phase 1+.

### MinIO
Project artifacts, snapshots, and generated outputs must be stored durably and served efficiently. MinIO's S3 API compatibility means the same code works against a local MinIO instance in development and against AWS S3, GCS, or Azure Blob Storage in production — with zero application changes. This is a critical future-proofing decision.

## Consequences

**What becomes easier:**
- PostgreSQL's `pgvector` extension enables vector similarity search for AI features in Phase 1+
- NATS JetStream enables event replay and audit logs without additional infrastructure
- MinIO's S3 API means cloud deployment (AWS/GCP/Azure) is a config change, not a rewrite
- All three services have excellent Docker images and health check support

**What becomes harder:**
- Schema changes require migration scripts (handled by the API service via a migration tool)
- NATS JetStream requires persistent volume configuration (handled in Phase 0.2)
- Teams unfamiliar with these tools will need onboarding

**New constraints introduced:**
- All data-producing services must publish events to NATS (enforced by convention)
- All binary artifact storage must go through MinIO, never the local filesystem
- Database schema changes must be versioned migrations (no ad-hoc ALTER statements)

## References

- [RFC 0001 — APFS](../rfc/0001-apfs.md)
- [RFC 0004 — Health Check Specification](../rfc/0004-health.md)
- [Infrastructure Contract](../infrastructure.md)
- NATS JetStream documentation: https://docs.nats.io/nats-concepts/jetstream
- MinIO S3 compatibility: https://min.io/product/s3-compatibility
- pgvector (future): https://github.com/pgvector/pgvector
