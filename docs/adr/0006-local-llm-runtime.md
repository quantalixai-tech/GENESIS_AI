# ADR-006 — Local LLM Runtime & Model Abstraction

| Field | Value |
|---|---|
| **ADR Number** | 0006 |
| **Title** | Local LLM Runtime and Model Abstraction Layer |
| **Status** | Accepted |
| **Date** | 2026-08-13 |
| **Phase** | 1.0 |

---

## Context

The platform requires an LLM abstraction layer that:
1. Routes calls to the correct provider (Ollama local, OpenAI, Anthropic, Google)
2. Never hardcodes model names — all calls go through `model_registry`
3. Tracks token usage and cost in every `ai_run` record
4. Supports streaming responses for the conversation UI

Options considered:
1. **Hand-rolled provider clients** — write `OllamaClient`, `OpenAIClient`, etc. manually
2. **LiteLLM** — unified Python library supporting 100+ providers with a single API surface
3. **LangChain** — heavyweight framework with its own abstractions

## Decision

**LiteLLM** as the provider abstraction layer, with **Ollama** as the primary local runtime (via Docker).

```python
# Resolved from model_registry, never hardcoded
import litellm
response = litellm.completion(
    model=f"ollama/{model_registry.model_id}",  # e.g., "ollama/llama3.2"
    messages=messages,
    stream=True,
)
```

Provider prefix conventions (set in `model_registry.provider`):
- `ollama` → `ollama/<model_id>` (local)
- `openai` → `<model_id>` (e.g., `gpt-4o`)
- `anthropic` → `anthropic/<model_id>`
- `google` → `gemini/<model_id>`

## Rationale

- **LiteLLM**: Eliminates the maintenance burden of per-provider clients. Handles retries, streaming, token counting, and cost estimation consistently across providers. Actively maintained with broad provider support.
- **Ollama**: Mature local runtime with a REST API compatible with OpenAI format. Supports llama, mistral, gemma, phi, codellama, and many others. Docker-deployable with GPU passthrough.
- **Not LangChain**: Excessive abstraction overhead; Genesis already has its own agent governance layer.

## Consequences

- Add `litellm` to `apps/api/pyproject.toml`
- Add Ollama to `infrastructure/docker/compose/docker-compose.ai.yml`
- `llm_service.py` wraps LiteLLM calls with `model_registry` lookup and `ai_run` token tracking
- Context window limits enforced by reading `model_registry.context_window`
- Fallback strategy: if local Ollama fails, fall back to configured cloud provider if API key present
- Model routing: orchestrator selects model based on task complexity and `agent_registry.model_id`
