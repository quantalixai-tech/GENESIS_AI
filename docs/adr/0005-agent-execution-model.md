# ADR-005 — Agent Execution Model

| Field | Value |
|---|---|
| **ADR Number** | 0005 |
| **Title** | Agent Execution Model |
| **Status** | Accepted |
| **Date** | 2026-08-13 |
| **Phase** | 1.0 |

---

## Context

Genesis agents (requirement extraction, code generation, repair, etc.) need an execution model that provides isolation, observability, parallelism, and governance (risk-level enforcement, approval gates).

Options considered:

1. **In-process** — agents run as async tasks within the FastAPI worker process
2. **NATS-dispatched** — agents are tasks published to NATS, consumed by the worker subprocess
3. **Dedicated container per agent run** — each agent invocation spins up a Docker container

## Decision

**NATS-dispatched tasks via the existing worker** (Option 2), with an async reply pattern using NATS JetStream.

The execution flow:
```
API Service
  → creates ai_run record (status=PENDING)
  → publishes AgentTask message to NATS subject (e.g., genesis.agents.requirement)
  → returns task ID to caller immediately (non-blocking)

Worker (asyncio)
  → receives AgentTask from NATS
  → updates ai_run status=RUNNING
  → executes agent logic
  → publishes AgentResult to reply subject
  → updates ai_run status=COMPLETED|FAILED

API/SSE stream
  → polls ai_run or receives NATS reply
  → streams result to frontend via SSE
```

## Rationale

- **Isolation**: Agent failures cannot crash the API process
- **Existing infrastructure**: NATS + worker are already deployed and working
- **Parallelism**: Multiple NATS consumers can process tasks concurrently without code changes
- **Observability**: Every task creates an `ai_run` record before dispatch — traceable from the moment of creation
- **Non-blocking API**: Callers receive a task ID immediately; progress is streamed separately
- **Risk enforcement**: The service layer checks `agent_registry.risk_level` and `requires_approval` before publishing — this cannot be bypassed by agent code

## Consequences

- Agent tasks are async — callers must poll or stream for results
- Worker must be resilient to message replay (idempotent handlers)
- NATS subject naming convention: `genesis.agents.<agent_type>` (e.g., `genesis.agents.requirement`)
- Maximum execution enforced by NATS message TTL + worker timeout wrapper
- Failed tasks are retried up to `agent_registry.max_retries` before escalation
