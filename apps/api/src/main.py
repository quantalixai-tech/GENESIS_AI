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

from fastapi import FastAPI
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
    version="0.3.0",
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

# System routes (no version prefix — stable contract for infra tooling)
from api.v1 import health as health_module  # noqa: E402

app.include_router(health_module.router, prefix="/api")

# Versioned API routes
from api.v1 import auth, projects, workspaces  # noqa: E402

api_v1_prefix = f"/api/{settings.api_version}"

app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(workspaces.router, prefix=api_v1_prefix)
app.include_router(projects.router, prefix=api_v1_prefix)


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
