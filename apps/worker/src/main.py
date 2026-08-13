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
import sys

import nats
from nats.errors import ConnectionClosedError, NoServersError, TimeoutError

from core.config import settings
from core.logging import get_logger

logger = get_logger("genesis.worker")

# ---------------------------------------------------------------------------
# Message handlers
# ---------------------------------------------------------------------------

async def message_handler(msg) -> None:
    """
    Default message handler for genesis.worker.> subject.
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

async def agent_invoke_handler(msg) -> None:
    """
    Handler for genesis.agent.invoke subject.
    """
    subject = msg.subject
    data = msg.data.decode("utf-8", errors="replace")
    
    logger.info("Agent invocation received", extra={"subject": subject})
    # TODO: Phase 4 AI Engine parsing and routing
    
    # Acknowledge the message if it's a JetStream msg
    try:
        await msg.ack()
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    logger.info(
        "Genesis Worker starting",
        extra={"nats_url": settings.nats_url, "environment": settings.genesis_env},
    )

    nc = None
    try:
        nc = await nats.connect(
            settings.nats_url,
            name="genesis-worker",
            max_reconnect_attempts=10,
            reconnect_time_wait=2,
            error_cb=_on_error,
            disconnected_cb=_on_disconnect,
            reconnected_cb=_on_reconnect,
            closed_cb=_on_close,
        )
        logger.info("Connected to NATS")

        sub = await nc.subscribe("genesis.worker.>", cb=message_handler)
        agent_sub = await nc.subscribe("genesis.agent.invoke", cb=agent_invoke_handler)
        logger.info("Subscribed to genesis.worker.> and genesis.agent.invoke")

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
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"FATAL ERROR: {e}")
