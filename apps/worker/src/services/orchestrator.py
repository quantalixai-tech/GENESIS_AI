import json

from agents.registry import get_agent_registry
from sqlmodel import Session

import genesis_db
from core.logging import get_logger

logger = get_logger(__name__)


async def process_agent_invoke(msg_data: str) -> None:
    """
    Process an incoming genesis.agent.invoke message.
    Payload expected:
    {
        "agent_key": "requirement_agent",
        "project_id": "uuid-string",
        "user_id": "uuid-string",
        "input_data": { ... }
    }
    """
    logger.info("Orchestrator received agent invocation")

    try:
        payload = json.loads(msg_data)
        agent_key = payload.get("agent_key")

        if not agent_key:
            logger.error("Missing agent_key in invocation payload")
            return

        with Session(genesis_db.engine) as session:
            # 1. Get the agent from the registry
            registry = get_agent_registry()
            agent = registry.get_agent(session, agent_key)

            # 2. Setup context
            import uuid

            from agents.base import AgentContext

            project_id_str = payload.get("project_id")
            user_id_str = payload.get("user_id")

            context = AgentContext(
                session=session,
                project_id=uuid.UUID(project_id_str) if project_id_str else None,
                triggered_by_user_id=uuid.UUID(user_id_str) if user_id_str else None,
            )

            input_data = payload.get("input_data", {})

            # 3. Execute
            logger.info(f"Executing agent {agent_key}")
            result = await agent.execute(context, input_data)

            if result.success:
                logger.info(f"Agent {agent_key} succeeded", extra={"run_id": str(context.run_id)})
            else:
                logger.error(
                    f"Agent {agent_key} failed",
                    extra={"error": result.error, "run_id": str(context.run_id)},
                )

    except json.JSONDecodeError:
        logger.error("Failed to decode agent invocation payload", extra={"payload": msg_data})
    except Exception as e:
        logger.exception(f"Orchestrator failed to process message: {e}")
