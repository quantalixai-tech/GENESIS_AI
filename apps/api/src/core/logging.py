"""
Genesis API — Structured Logging

Configures structured JSON logging for the API and worker processes.
Every log record includes:
    - timestamp (ISO 8601, UTC)
    - level
    - logger name
    - message
    - request_id (if available in context)
    - trace_id (if available in context)

Usage:
    from core.logging import get_logger
    logger = get_logger(__name__)
    logger.info("Project created", extra={"project_id": str(project.id)})
"""

import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any

# Context variables for per-request correlation IDs.
# These are set by the request ID middleware and automatically
# included in every log record via the filter below.
request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


class ContextFilter(logging.Filter):
    """
    Injects request_id and trace_id from context variables into every log record.
    This is what ties all log lines for a single request together.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get("-")
        record.trace_id = trace_id_var.get("-")
        return True


class StructuredFormatter(logging.Formatter):
    """
    Formats log records as structured key=value lines.
    In a production environment, these can be replaced with JSON via a different formatter.
    """

    def format(self, record: logging.LogRecord) -> str:
        self.ensure_context(record)
        timestamp = datetime.now(timezone.utc).isoformat()
        level = record.levelname
        logger = record.name
        message = record.getMessage()
        request_id = getattr(record, "request_id", "-")
        trace_id = getattr(record, "trace_id", "-")

        line = (
            f"timestamp={timestamp} level={level} logger={logger} "
            f'request_id={request_id} trace_id={trace_id} msg="{message}"'
        )

        # Append any extra fields passed via the `extra` dict
        for key, value in vars(record).items():
            if key not in _STANDARD_LOG_RECORD_ATTRS and not key.startswith("_"):
                line += f" {key}={value}"

        if record.exc_info:
            line += "\n" + self.formatException(record.exc_info)

        return line

    @staticmethod
    def ensure_context(record: logging.LogRecord) -> None:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        if not hasattr(record, "trace_id"):
            record.trace_id = "-"


# Standard LogRecord attributes to exclude from extra fields output
_STANDARD_LOG_RECORD_ATTRS: set[str] = {
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "request_id", "trace_id",
    "taskName",
}


def configure_logging(log_level: str = "info") -> None:
    """
    Configure the root logger for the Genesis platform.
    Call this once at application startup.
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(level)
    handler.addFilter(ContextFilter())
    handler.setFormatter(StructuredFormatter())

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    # Remove any pre-existing handlers (e.g., from uvicorn)
    root_logger.handlers.clear()
    root_logger.addHandler(handler)

    # Suppress noisy library loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Return a named logger. Prefer this over logging.getLogger() directly.

    Example:
        logger = get_logger(__name__)
        logger.info("Workspace created", extra={"workspace_id": str(workspace.id)})
    """
    return logging.getLogger(name)
