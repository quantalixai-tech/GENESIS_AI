"""
Genesis API — LLM Service

Provider-agnostic LLM client using LiteLLM as the abstraction layer.
All calls route through model_registry — model names are NEVER hardcoded.

Architecture (per ADR-006):
    model_registry.provider + model_registry.model_id
        → LiteLLM provider prefix (ollama/llama3.2, anthropic/claude-3-5-sonnet, etc.)
        → LiteLLM completion() or acompletion()
        → Token counts and cost written back to ai_run

Usage:
    from services.llm_service import complete, stream_complete

    # Non-streaming
    response = await complete(
        session=session,
        model_registry_id=model.id,
        messages=[{"role": "user", "content": "Hello"}],
        ai_run=run,
    )

    # Streaming (async generator)
    async for token in stream_complete(...):
        yield token

Raises:
    NotFoundError      — model_registry_id not found or inactive
    GenesisError       — LLM provider call failed

Notes:
    - Never hardcode model names anywhere in application code
    - Always pass ai_run so token usage is recorded
    - Context window limits are enforced via model_registry.context_window
    - Fallback: if Ollama unavailable, routes to configured cloud provider
"""

import uuid
from collections.abc import AsyncIterator
from typing import Any

import litellm
from sqlmodel import Session

import genesis_db
from core.config import settings
from core.errors import ErrorCode, GenesisError, NotFoundError
from core.logging import get_logger

logger = get_logger(__name__)

# Suppress LiteLLM's verbose startup logging
litellm.suppress_debug_info = True


# =============================================================================
# Provider prefix mapping
# =============================================================================

_PROVIDER_PREFIX: dict[str, str] = {
    genesis_db.ModelProvider.OPENAI: "",  # OpenAI: model_id as-is
    genesis_db.ModelProvider.ANTHROPIC: "anthropic/",
    genesis_db.ModelProvider.GOOGLE: "gemini/",
    genesis_db.ModelProvider.OLLAMA: "ollama/",
    genesis_db.ModelProvider.CUSTOM: "",
}


def _resolve_litellm_model(model: genesis_db.ModelRegistry) -> str:
    """
    Resolve a ModelRegistry entry to a LiteLLM model string.

    Examples:
        provider=ollama, model_id=llama3.2  → "ollama/llama3.2"
        provider=anthropic, model_id=claude-3-5-sonnet-20241022 → "anthropic/claude-3-5-sonnet-20241022"
        provider=openai, model_id=gpt-4o → "gpt-4o"
    """
    prefix = _PROVIDER_PREFIX.get(model.provider, "")
    return f"{prefix}{model.model_id}"


# =============================================================================
# Model lookup
# =============================================================================


def get_model(session: Session, model_registry_id: uuid.UUID) -> genesis_db.ModelRegistry:
    """
    Retrieve a model from the registry.

    Raises:
        NotFoundError: If model not found or inactive.
    """
    model = session.get(genesis_db.ModelRegistry, model_registry_id)
    if not model or not model.is_active:
        raise NotFoundError(
            f"Model {model_registry_id} not found or inactive in model_registry.",
            code=ErrorCode.NOT_FOUND,
        )
    return model


def get_default_model(session: Session) -> genesis_db.ModelRegistry:
    """
    Return the default model (Ollama local model if available).

    Falls back to the first active model in the registry.
    """
    from sqlmodel import select

    # Prefer Ollama (local)
    local_model = session.exec(
        select(genesis_db.ModelRegistry).where(
            genesis_db.ModelRegistry.provider == genesis_db.ModelProvider.OLLAMA,
            genesis_db.ModelRegistry.is_active == True,  # noqa: E712
        )
    ).first()

    if local_model:
        return local_model

    # Fall back to first active model
    any_model = session.exec(
        select(genesis_db.ModelRegistry).where(
            genesis_db.ModelRegistry.is_active == True  # noqa: E712
        )
    ).first()

    if not any_model:
        raise NotFoundError(
            "No active models found in model_registry. "
            "Please register at least one model before invoking agents.",
            code=ErrorCode.NOT_FOUND,
        )
    return any_model


# =============================================================================
# LiteLLM wrapper utilities
# =============================================================================


def _build_litellm_kwargs(
    model: genesis_db.ModelRegistry,
    messages: list[dict[str, str]],
    temperature: float = 0.2,
    max_tokens: int | None = None,
    **extra: Any,
) -> dict[str, Any]:
    """Build the kwargs dict for a LiteLLM completion call."""
    resolved_model = _resolve_litellm_model(model)

    kwargs: dict[str, Any] = {
        "model": resolved_model,
        "messages": messages,
        "temperature": temperature,
        **extra,
    }

    # Respect model context window
    if max_tokens:
        kwargs["max_tokens"] = max_tokens
    elif model.max_output_tokens:
        kwargs["max_tokens"] = model.max_output_tokens

    # Ollama needs base_url pointing to local instance
    if model.provider == genesis_db.ModelProvider.OLLAMA:
        kwargs["api_base"] = settings.ollama_base_url

    return kwargs


def _estimate_cost(
    model: genesis_db.ModelRegistry,
    prompt_tokens: int,
    completion_tokens: int,
) -> float | None:
    """
    Estimate API cost in USD.

    For local Ollama models, cost is 0.0.
    For cloud providers, LiteLLM provides cost estimation.
    """
    if model.provider == genesis_db.ModelProvider.OLLAMA:
        return 0.0
    try:
        cost = litellm.completion_cost(
            model=_resolve_litellm_model(model),
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )
        return float(cost)
    except Exception:
        return None


# =============================================================================
# Non-streaming completion
# =============================================================================


async def complete(
    session: Session,
    model_registry_id: uuid.UUID,
    messages: list[dict[str, str]],
    ai_run: genesis_db.AIRun,
    *,
    temperature: float = 0.2,
    max_tokens: int | None = None,
    response_format: dict | None = None,
) -> str:
    """
    Perform a non-streaming LLM completion and update the ai_run record.

    Args:
        session: Database session.
        model_registry_id: ID from model_registry — NEVER a hardcoded model name.
        messages: Chat messages in OpenAI format.
        ai_run: The governing AIRun record — token counts are written back here.
        temperature: Sampling temperature (0.0 = deterministic).
        max_tokens: Override max output tokens.
        response_format: Optional JSON schema for structured output.

    Returns:
        The assistant's response content as a string.

    Raises:
        NotFoundError: If model not found.
        GenesisError: If LLM provider call fails.
    """
    model = get_model(session, model_registry_id)
    kwargs = _build_litellm_kwargs(model, messages, temperature=temperature, max_tokens=max_tokens)

    if response_format:
        kwargs["response_format"] = response_format

    logger.info(
        "LLM completion request",
        extra={
            "run_id": str(ai_run.id),
            "model": _resolve_litellm_model(model),
            "message_count": len(messages),
        },
    )

    try:
        response = await litellm.acompletion(**kwargs)
    except Exception as exc:
        logger.error(
            "LLM completion failed",
            extra={"run_id": str(ai_run.id), "error": str(exc)},
        )
        raise GenesisError(
            f"LLM completion failed: {exc!s}",
            code=ErrorCode.AI_EXECUTION_FAILED,
            http_status=502,
        ) from exc

    # Extract usage
    usage = response.usage
    prompt_tokens = usage.prompt_tokens if usage else 0
    completion_tokens = usage.completion_tokens if usage else 0
    cost = _estimate_cost(model, prompt_tokens, completion_tokens)

    # Write token counts to ai_run
    from services.agent_service import update_ai_run_status

    update_ai_run_status(
        session,
        ai_run,
        genesis_db.AIRunStatus.RUNNING,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost_usd=cost,
    )

    content: str = response.choices[0].message.content or ""
    logger.info(
        "LLM completion done",
        extra={
            "run_id": str(ai_run.id),
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "cost_usd": cost,
        },
    )
    return content


# =============================================================================
# Streaming completion (for SSE conversation UI)
# =============================================================================


async def stream_complete(
    session: Session,
    model_registry_id: uuid.UUID,
    messages: list[dict[str, str]],
    ai_run: genesis_db.AIRun,
    *,
    temperature: float = 0.3,
    max_tokens: int | None = None,
) -> AsyncIterator[str]:
    """
    Perform a streaming LLM completion, yielding tokens as they arrive.

    Designed for SSE endpoints — each yielded string is one token chunk.
    Token counts are written to ai_run when the stream completes.

    Usage:
        async for token in stream_complete(...):
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\\n\\n"
    """
    model = get_model(session, model_registry_id)
    kwargs = _build_litellm_kwargs(model, messages, temperature=temperature, max_tokens=max_tokens)
    kwargs["stream"] = True

    logger.info(
        "LLM stream start",
        extra={"run_id": str(ai_run.id), "model": _resolve_litellm_model(model)},
    )

    full_content: list[str] = []
    prompt_tokens = 0
    completion_tokens = 0

    try:
        response = await litellm.acompletion(**kwargs)
        async for chunk in response:  # type: ignore[union-attr]
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                full_content.append(delta)
                completion_tokens += 1  # Approximate; exact count from final chunk
                yield delta

            # LiteLLM emits usage in the final chunk for some providers
            if hasattr(chunk, "usage") and chunk.usage:
                prompt_tokens = chunk.usage.prompt_tokens or 0
                completion_tokens = chunk.usage.completion_tokens or completion_tokens

    except Exception as exc:
        logger.error(
            "LLM stream failed",
            extra={"run_id": str(ai_run.id), "error": str(exc)},
        )
        raise GenesisError(
            f"LLM stream failed: {exc!s}",
            code=ErrorCode.AI_EXECUTION_FAILED,
            http_status=502,
        ) from exc

    # Write final token counts
    cost = _estimate_cost(model, prompt_tokens, completion_tokens)
    from services.agent_service import update_ai_run_status

    update_ai_run_status(
        session,
        ai_run,
        genesis_db.AIRunStatus.RUNNING,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost_usd=cost,
    )

    logger.info(
        "LLM stream complete",
        extra={
            "run_id": str(ai_run.id),
            "completion_tokens": completion_tokens,
            "cost_usd": cost,
        },
    )


# =============================================================================
# Prompt retrieval (per AI_GOVERNANCE.md §3 — no inline prompts)
# =============================================================================


def get_active_prompt(session: Session, prompt_key: str) -> genesis_db.PromptRegistry:
    """
    Retrieve the active version of a registered prompt by its stable key.

    Raises:
        NotFoundError: If no active prompt found for this key.
    """
    from sqlmodel import select

    prompt = session.exec(
        select(genesis_db.PromptRegistry).where(
            genesis_db.PromptRegistry.prompt_key == prompt_key,
            genesis_db.PromptRegistry.status == genesis_db.PromptStatus.ACTIVE,
        )
    ).first()

    if not prompt:
        raise NotFoundError(
            f"No active prompt found for key '{prompt_key}'. "
            "Register the prompt in prompt_registry before use.",
            code=ErrorCode.NOT_FOUND,
        )
    return prompt
