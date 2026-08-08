"""
Genesis Worker — NATS Message Consumer

Subscribes to NATS JetStream subjects and processes platform events.

Current phase (0.3): Foundation stub — connects to NATS, subscribes to
genesis.worker.>, and logs received messages. No real processing yet.

Architecture (future):
    NATS subject       → Handler function → Service → DB / AI Agent
    genesis.project.*  → project_handlers
    genesis.agent.*    → agent_handlers
    genesis.build.*    → build_handlers

Environment variables:
    NATS_URL        — NATS server URL (default: nats://localhost:4222)
    DATABASE_URL    — PostgreSQL connection string
    GENESIS_ENV     — Platform environment
    GENESIS_LOG_LEVEL — Log level
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timezone

import nats
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError

# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

log_level_name = os.environ.get("GENESIS_LOG_LEVEL", "info").upper()
log_level = getattr(logging, log_level_name, logging.INFO)

logging.basicConfig(
    level=log_level,
    format="timestamp=%(asctime)s level=%(levelname)s logger=%(name)s msg=\"%(message)s\"",
    datefmt="%Y-%m-%dT%H:%M:%SZ",
    stream=sys.stdout,
)
logger = logging.getLogger("genesis.worker")

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

NATS_URL = os.environ.get("NATS_URL", "nats://localhost:4222")
GENESIS_ENV = os.environ.get("GENESIS_ENV", "development")


# ---------------------------------------------------------------------------
# Message handlers
# ---------------------------------------------------------------------------


async def message_handler(msg) -> None:
    """
    Default message handler for genesis.worker.> subject.

    Phase 0.3: Logs received messages and acknowledges them.
    Phase 1.0+: Routes to domain-specific handlers based on subject.
    """
    subject = msg.subject
    data = msg.data.decode("utf-8", errors="replace")

    logger.info(
        "Message received",
        extra={
            "subject": subject,
            "data_length": len(data),
        },
    )

    # TODO(phase-1.0): Route to domain handlers based on subject prefix
    # Examples:
    #   genesis.project.created   → project_handlers.handle_project_created
    #   genesis.agent.run.start   → agent_handlers.handle_agent_run_start
    #   genesis.build.complete    → build_handlers.handle_build_complete


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    logger.info(
        "Genesis Worker starting",
        extra={"nats_url": NATS_URL, "environment": GENESIS_ENV},
    )

    nc = None
    try:
        nc = await nats.connect(
            NATS_URL,
            name="genesis-worker",
            # Reconnection strategy: attempt up to 10 times with 2s delay
            max_reconnect_attempts=10,
            reconnect_time_wait=2,
            error_cb=_on_error,
            disconnected_cb=_on_disconnect,
            reconnected_cb=_on_reconnect,
            closed_cb=_on_close,
        )
        logger.info("Connected to NATS")

        sub = await nc.subscribe("genesis.worker.>", cb=message_handler)
        logger.info("Subscribed to genesis.worker.>")

        # Keep the worker alive — rely on NATS callbacks for error handling
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Worker shutdown signal received")
            await sub.unsubscribe()

    except NoServersError:
        logger.error("Could not connect to NATS — no servers available", extra={"nats_url": NATS_URL})
        sys.exit(1)
    except Exception as exc:
        logger.exception("Unexpected worker error: %s", exc)
        sys.exit(1)
    finally:
        if nc and not nc.is_closed:
            await nc.drain()
            logger.info("NATS connection drained and closed")


async def _on_error(exc: Exception) -> None:
    logger.error("NATS error", extra={"error": str(exc)})


async def _on_disconnect() -> None:
    logger.warning("NATS disconnected — attempting reconnect")


async def _on_reconnect() -> None:
    logger.info("NATS reconnected")


async def _on_close() -> None:
    logger.info("NATS connection closed")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker interrupted by user")
