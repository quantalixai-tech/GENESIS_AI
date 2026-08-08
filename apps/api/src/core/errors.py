"""
Genesis API — Error Model

Defines a consistent error response structure across all API endpoints.

Error Response Format:
    {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "Human-readable description",
            "details": [...]  // Optional array of field-level issues
        }
    }

Error codes are uppercase snake_case strings that clients can pattern-match on.
HTTP status codes carry semantic meaning. Error codes carry application meaning.

DO NOT leak:
    - Stack traces (in production)
    - Internal file paths
    - SQL query details
    - Infrastructure hostnames
    - Secrets or credentials
"""

from enum import StrEnum
from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ErrorCode(StrEnum):
    """
    Canonical error codes for the Genesis API.
    Add new codes here when adding new error conditions.
    Do not use ad-hoc string codes in route handlers.
    """

    # --- Authentication / Authorization ---
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    TOKEN_INVALID = "TOKEN_INVALID"

    # --- Validation ---
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"

    # --- Not Found ---
    NOT_FOUND = "NOT_FOUND"
    USER_NOT_FOUND = "USER_NOT_FOUND"
    PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
    WORKSPACE_NOT_FOUND = "WORKSPACE_NOT_FOUND"

    # --- Conflicts ---
    CONFLICT = "CONFLICT"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"

    # --- Server Errors ---
    INTERNAL_ERROR = "INTERNAL_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"

    # --- AI / Agent ---
    AI_EXECUTION_FAILED = "AI_EXECUTION_FAILED"
    AGENT_NOT_FOUND = "AGENT_NOT_FOUND"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    APPROVAL_REQUIRED = "APPROVAL_REQUIRED"


class ErrorDetail(BaseModel):
    """Individual field-level or item-level error detail."""

    field: str | None = None
    message: str
    code: str | None = None


class ErrorBody(BaseModel):
    """The `error` object nested inside the error response."""

    code: str
    message: str
    details: list[ErrorDetail] | None = None


class ErrorResponse(BaseModel):
    """Top-level error response envelope."""

    error: ErrorBody


class GenesisError(Exception):
    """
    Base exception for all Genesis application errors.

    Raise GenesisError subclasses from service and domain code.
    The exception handler converts these to ErrorResponse JSON automatically.

    Example:
        raise NotFoundError("Project not found", code=ErrorCode.PROJECT_NOT_FOUND)
    """

    def __init__(
        self,
        message: str,
        code: ErrorCode = ErrorCode.INTERNAL_ERROR,
        http_status: int = 500,
        details: list[ErrorDetail] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.http_status = http_status
        self.details = details


class NotFoundError(GenesisError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.NOT_FOUND) -> None:
        super().__init__(message, code=code, http_status=404)


class ConflictError(GenesisError):
    def __init__(self, message: str, code: ErrorCode = ErrorCode.CONFLICT) -> None:
        super().__init__(message, code=code, http_status=409)


class ValidationError(GenesisError):
    def __init__(
        self,
        message: str,
        details: list[ErrorDetail] | None = None,
        code: ErrorCode = ErrorCode.VALIDATION_ERROR,
    ) -> None:
        super().__init__(message, code=code, http_status=422, details=details)


class UnauthorizedError(GenesisError):
    def __init__(self, message: str = "Unauthorized", code: ErrorCode = ErrorCode.UNAUTHORIZED) -> None:
        super().__init__(message, code=code, http_status=401)


class ForbiddenError(GenesisError):
    def __init__(self, message: str = "Forbidden", code: ErrorCode = ErrorCode.FORBIDDEN) -> None:
        super().__init__(message, code=code, http_status=403)


class PolicyViolationError(GenesisError):
    """Raised when an AI agent attempts an action that violates a governance policy."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code=ErrorCode.POLICY_VIOLATION, http_status=403)


class ApprovalRequiredError(GenesisError):
    """Raised when a high-risk AI action requires human approval before proceeding."""

    def __init__(self, message: str) -> None:
        super().__init__(message, code=ErrorCode.APPROVAL_REQUIRED, http_status=202)


def make_error_response(
    code: str,
    message: str,
    http_status: int,
    details: list[ErrorDetail] | None = None,
) -> JSONResponse:
    """Construct a JSONResponse with the standard Genesis error envelope."""
    body = ErrorResponse(
        error=ErrorBody(code=code, message=message, details=details)
    )
    return JSONResponse(status_code=http_status, content=body.model_dump(exclude_none=True))


async def genesis_error_handler(request: Request, exc: GenesisError) -> JSONResponse:
    """FastAPI exception handler for GenesisError and subclasses."""
    return make_error_response(
        code=exc.code,
        message=exc.message,
        http_status=exc.http_status,
        details=exc.details,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Catch-all handler for unexpected exceptions.
    Logs the full exception but returns a generic error to the client.
    DO NOT leak exception details to the client in production.
    """
    from core.logging import get_logger
    from core.config import settings

    logger = get_logger(__name__)
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)

    message = (
        str(exc) if settings.is_development
        else "An unexpected error occurred. Please try again later."
    )

    return make_error_response(
        code=ErrorCode.INTERNAL_ERROR,
        message=message,
        http_status=500,
    )
