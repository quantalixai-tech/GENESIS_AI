import json
from typing import Any, TypeVar
from pydantic import BaseModel
import ollama
from ollama import AsyncClient

from core.config import settings
from core.logging import get_logger

logger = get_logger(__name__)

T = TypeVar("T", bound=BaseModel)

class AIServiceError(Exception):
    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.details = details

async def generate_completion(
    model: str,
    messages: list[dict[str, str]],
    response_schema: type[T] | None = None,
) -> tuple[str | T, dict[str, Any]]:
    """
    Generate a completion using Ollama.
    """
    client = AsyncClient(host=settings.ollama_base_url)
    
    try:
        logger.debug(f"Calling Ollama model {model}")
        
        options = {}
        chat_kwargs = {
            "model": model,
            "messages": messages,
            "options": options,
        }
        if response_schema:
            chat_kwargs["format"] = response_schema.model_json_schema()
            
        response = await client.chat(**chat_kwargs)
        
        content = response["message"]["content"]
        
        usage_stats = {
            "prompt_tokens": response.get("prompt_eval_count", 0),
            "completion_tokens": response.get("eval_count", 0),
            "total_tokens": response.get("prompt_eval_count", 0) + response.get("eval_count", 0),
            "duration_ms": response.get("eval_duration", 0) / 1_000_000 if response.get("eval_duration") else 0
        }
        
        if response_schema:
            try:
                parsed_data = json.loads(content)
                validated_data = response_schema.model_validate(parsed_data)
                return validated_data, usage_stats
            except Exception as e:
                logger.error("Failed to parse/validate JSON from LLM output", extra={"content": content})
                raise AIServiceError("LLM output validation failed", details={"error": str(e)})
                
        return content, usage_stats
        
    except Exception as e:
        logger.error(f"Unexpected AI service error: {e}")
        raise AIServiceError(f"Unexpected AI service error: {str(e)}")
