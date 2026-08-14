import json
from typing import Any, TypeVar

import ollama
from ollama import AsyncClient
from pydantic import BaseModel

from core.config import settings
from core.errors import ErrorCode, GenesisError
from core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)


class AIServiceError(GenesisError):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            code=ErrorCode.INTERNAL_SERVER_ERROR,
            details=details,
        )


async def generate_completion(
    model: str,
    messages: list[dict[str, str]],
    response_schema: type[T] | None = None,
) -> tuple[str | T, dict[str, Any]]:
    """
    Generate a completion using Ollama.

    If response_schema is provided, the output will be parsed and validated against it.
    Returns a tuple of (content, usage_stats).
    """
    client = AsyncClient(host=settings.ollama_base_url)

    try:
        # Prepare options
        options = {}
        if response_schema:
            options["format"] = "json"

        logger.debug(f"Calling Ollama model {model}", extra={"messages_count": len(messages)})

        response = await client.chat(
            model=model,
            messages=messages,
            options=options,
        )

        content = response["message"]["content"]

        usage_stats = {
            "prompt_tokens": response.get("prompt_eval_count", 0),
            "completion_tokens": response.get("eval_count", 0),
            "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
            "duration_ms": response.get("eval_duration", 0) / 1_000_000
            if response.get("eval_duration")
            else 0,
        }

        if response_schema:
            try:
                parsed_data = json.loads(content)
                validated_data = response_schema.model_validate(parsed_data)
                return validated_data, usage_stats
            except json.JSONDecodeError as e:
                logger.error("Failed to parse JSON from LLM output", extra={"content": content})
                raise AIServiceError(
                    "LLM returned malformed JSON", details={"error": str(e)}
                ) from e
            except Exception as e:
                logger.error(
                    "Failed to validate LLM output against schema", extra={"error": str(e)}
                )
                raise AIServiceError(
                    "LLM output validation failed", details={"error": str(e)}
                ) from e

        return content, usage_stats

    except ollama.ResponseError as e:
        logger.error(f"Ollama API error: {e}")
        raise AIServiceError(f"Ollama API error: {e.error}") from e
    except Exception as e:
        logger.error(f"Unexpected AI service error: {e}")
        raise AIServiceError(f"Unexpected AI service error: {str(e)}") from e
