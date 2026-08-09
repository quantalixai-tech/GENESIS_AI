"""
Genesis API — Health Check

Returns the actual health of all critical platform dependencies.

HTTP 200 = all checks passed → service is healthy
HTTP 503 = one or more critical dependencies are unavailable → service degraded

DO NOT return hardcoded "connected" — load balancers and monitors rely on
this endpoint to route traffic and trigger alerts.

Checks performed:
    - Database: executes SELECT 1 to verify connectivity

Future checks to add when services are integrated:
    - NATS connectivity
    - MinIO connectivity
"""

from fastapi import APIRouter
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlmodel import Session

import genesis_db
from core.config import settings
from core.logging import get_logger

router = APIRouter(tags=["system"])
logger = get_logger(__name__)


@router.get("/health", summary="Health check")
def health_check() -> JSONResponse:
    """
    Return the health status of the Genesis API and its dependencies.

    Returns HTTP 200 when all critical checks pass.
    Returns HTTP 503 when any critical dependency is unavailable.
    """
    db_status = "unknown"
    overall_status = "ok"
    http_status = 200

    # --- Database check ---
    try:
        with Session(genesis_db.engine) as session:
            session.exec(text("SELECT 1"))  # type: ignore[call-overload]
        db_status = "connected"
    except Exception as exc:
        logger.error(
            "Health check: database connectivity failure",
            extra={"error": str(exc)},
        )
        db_status = "unreachable"
        overall_status = "degraded"
        http_status = 503

    body = {
        "status": overall_status,
        "version": "0.3.0",
        "environment": settings.genesis_env,
        "dependencies": {
            "database": db_status,
        },
    }

    return JSONResponse(content=body, status_code=http_status)
