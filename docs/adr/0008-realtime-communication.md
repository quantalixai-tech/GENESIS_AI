# ADR-008 — Real-Time Communication Model

| Field | Value |
|---|---|
| **ADR Number** | 0008 |
| **Title** | Real-Time Communication Model (Agent Activity, LLM Streaming) |
| **Status** | Accepted |
| **Date** | 2026-08-13 |
| **Phase** | 1.0 |

---

## Context

The workspace UI needs real-time updates for:
1. Streaming LLM responses (conversation panel)
2. Agent activity status (agent panel)
3. Validation progress and results

Options considered:
1. **WebSockets** — bidirectional, full-duplex
2. **Server-Sent Events (SSE)** — unidirectional server→client, HTTP/1.1+
3. **HTTP polling** — client polls periodically
4. **Long polling** — client holds open request until event

## Decision

**SSE (Server-Sent Events)** via FastAPI `StreamingResponse` for both LLM token streaming and agent activity events.

```python
# FastAPI SSE endpoint
@router.get("/conversations/{id}/stream")
async def stream_conversation(id: UUID) -> StreamingResponse:
    async def event_generator() -> AsyncIterator[str]:
        async for token in llm_service.stream_response(conversation_id=id):
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")
```

Event types sent over SSE:
- `token` — LLM response token (streaming)
- `agent_start` — agent invocation began
- `agent_complete` — agent finished
- `agent_error` — agent failed
- `validation_update` — validation step result
- `approval_required` — human approval needed
- `project_status` — project status changed

## Rationale

- **SSE over WebSockets**: Unidirectional is sufficient — the client sends messages via REST POST, server streams responses. SSE is simpler, works through standard HTTP proxies, and requires no special protocol handling.
- **Not polling**: 1–2s polling latency is unacceptable for LLM token streaming where sub-100ms response matters for UX.
- **FastAPI native**: `StreamingResponse` with `text/event-stream` is idiomatic FastAPI with no extra libraries.
- **Reconnection**: SSE has built-in browser reconnection with `Last-Event-ID` support.

## Consequences

- Add SSE endpoints: `GET /api/v1/projects/{id}/stream` and `GET /api/v1/conversations/{id}/stream`
- Frontend uses native `EventSource` API — no library required
- Worker publishes events to a NATS subject; API SSE handler subscribes and forwards
- Event stream closed when conversation complete or client disconnects
- CORS headers must include `text/event-stream` content type
