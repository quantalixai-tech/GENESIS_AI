"""
Genesis API — Request Middleware

Provides:
    1. RequestIDMiddleware — generates a unique request_id for every HTTP request,
       injects it into the response headers and logging context.

The request_id flows through:
    HTTP Request → Middleware → Context Variable → Logger → Response Header

Clients can use the X-Request-ID response header to correlate their requests
with server-side log entries.
"""

import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from core.logging import get_logger, request_id_var, trace_id_var

logger = get_logger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"
TRACE_ID_HEADER = "X-Trace-ID"


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Assigns a unique request_id to every incoming HTTP request.

    The request_id is:
    - Read from the X-Request-ID header if provided by the client (e.g., API gateway)
    - Generated as a new UUID4 if not provided

    The ID is:
    - Stored in a ContextVar so all logging within the request automatically includes it
    - Written to the X-Request-ID response header so clients can correlate requests
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        # Accept a request ID from upstream (e.g., load balancer, API gateway)
        # or generate a fresh one
        incoming_request_id = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming_request_id or str(uuid.uuid4())

        # Accept a trace ID from upstream for distributed tracing integration
        incoming_trace_id = request.headers.get(TRACE_ID_HEADER)
        trace_id = incoming_trace_id or request_id  # default: same as request_id

        # Inject into context variables — all log statements in this request
        # will automatically include these values
        request_id_token = request_id_var.set(request_id)
        trace_id_token = trace_id_var.set(trace_id)

        try:
            logger.debug(
                "Request started",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                },
            )

            response = await call_next(request)

            # Attach correlation IDs to response headers
            response.headers[REQUEST_ID_HEADER] = request_id
            response.headers[TRACE_ID_HEADER] = trace_id

            logger.debug(
                "Request completed",
                extra={
                    "method": request.method,
                    "path": request.url.path,
                    "status_code": response.status_code,
                },
            )

            return response

        finally:
            # Always reset context variables after request completes
            request_id_var.reset(request_id_token)
            trace_id_var.reset(trace_id_token)
