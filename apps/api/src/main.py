"""
Genesis API — Application Entry Point

Constructs the FastAPI application with:
    - Centralized configuration (pydantic-settings)
    - Structured logging
    - Request ID middleware (X-Request-ID correlation)
    - CORS restricted to configured origins (not wildcard)
    - Versioned API routes under /api/v1/
    - Structured error handlers (GenesisError → JSON error envelope)
    - Health check at /api/health (no version prefix — for load balancers)

Architecture:
    HTTP Request
        → RequestIDMiddleware (assigns request_id, injects into logging context)
        → CORS Middleware
        → Route Handler (thin — no business logic)
            → Service (business logic, authorization)
                → Repository / DB (genesis_db)
        → Error Handler (GenesisError → structured JSON)
        → HTTP Response (with X-Request-ID header)
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from core.config import settings
from core.errors import GenesisError, genesis_error_handler, unhandled_exception_handler
from core.logging import configure_logging, get_logger
from core.middleware import RequestIDMiddleware

# Initialize logging before anything else so all startup messages are captured
configure_logging(settings.genesis_log_level)
logger = get_logger(__name__)


# ---------------------------------------------------------------------------
# Lifespan — replaces deprecated @app.on_event("startup/shutdown")
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Application lifespan context manager.

    Code before `yield` runs at startup.
    Code after `yield` runs at shutdown.
    """
    # --- Startup ---
    logger.info(
        "Genesis API starting",
        extra={
            "environment": settings.genesis_env,
            "version": "0.3.0",
            "cors_origins": settings.cors_origins,
        },
    )

    yield  # Application runs here

    # --- Shutdown ---
    logger.info("Genesis API shutting down")


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version="1.0.0",
    lifespan=lifespan,
    # Disable auto-generated docs in production for reduced attack surface
    docs_url="/docs" if not settings.is_production else None,
    redoc_url="/redoc" if not settings.is_production else None,
    openapi_url="/openapi.json" if not settings.is_production else None,
)

# ---------------------------------------------------------------------------
# Middleware — order matters: outermost = first to process request
# ---------------------------------------------------------------------------

# 1. Request ID middleware — must be first so all subsequent middleware
#    and handlers have access to the request_id context variable
app.add_middleware(RequestIDMiddleware)

# 2. CORS — restricted to configured origins, NOT wildcard
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Request-ID", "X-Trace-ID"],
)

# ---------------------------------------------------------------------------
# Exception handlers
# ---------------------------------------------------------------------------

app.add_exception_handler(GenesisError, genesis_error_handler)
app.add_exception_handler(Exception, unhandled_exception_handler)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

# NOTE: Route imports are intentionally placed after configure_logging() above.
# Route modules reference settings/logging at module level, so they must be
# imported after the logging subsystem is initialized.
from api.v1 import agents  # noqa: E402, I001
from api.v1 import auth  # noqa: E402, I001
from api.v1 import conversations  # noqa: E402, I001
from api.v1 import git  # noqa: E402, I001
from api.v1 import health as health_module  # noqa: E402, I001
from api.v1 import preview  # noqa: E402, I001
from api.v1 import projects  # noqa: E402, I001
from api.v1 import workspaces  # noqa: E402, I001
from core.security import get_current_user  # noqa: E402, I001



# API v1 Router Setup
api_v1_prefix = "/api/v1"
protected = [Depends(get_current_user)]

app.include_router(health_module.router, prefix="/api")
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(workspaces.router, prefix=api_v1_prefix, dependencies=protected)
app.include_router(projects.router, prefix=api_v1_prefix, dependencies=protected)
app.include_router(conversations.router, prefix=api_v1_prefix, dependencies=protected)
app.include_router(conversations.requirements_router, prefix=api_v1_prefix, dependencies=protected)
app.include_router(agents.router, prefix=api_v1_prefix, dependencies=protected)
app.include_router(git.router, prefix=api_v1_prefix, dependencies=protected)
app.include_router(preview.router, prefix=api_v1_prefix, dependencies=protected)


# ---------------------------------------------------------------------------
# Local development entrypoint
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8080,
        reload=settings.is_development,
        log_level=settings.genesis_log_level,
    )
