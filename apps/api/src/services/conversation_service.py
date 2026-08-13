"""
Genesis API — Conversation Service

Manages the conversational requirement discovery flow.

Responsibilities:
    - Create and manage conversations for a project
    - Store and retrieve messages (user, assistant, agent)
    - Stream AI responses via the LLM service
    - Extract requirements from user messages (via RequirementAgent)
    - Update project status based on conversation state

This module does NOT:
    - Handle HTTP or SSE transport
    - Contain prompt content (prompts are in prompt_registry)
    - Process business logic outside conversation domain

Architecture:
    Route handler
        → conversation_service (this module)
            → llm_service (LiteLLM via model_registry)
            → agent_service (dispatch RequirementAgent via NATS)
            → DB: conversation, conversation_message, requirement

See: docs/AI_GOVERNANCE.md, docs/APPLICATION_FLOW.md §4
"""

import uuid
from collections.abc import AsyncIterator

import sqlalchemy as sa
from sqlmodel import Session, select

import genesis_db
from core.errors import ErrorCode, NotFoundError
from core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Conversation management
# =============================================================================


def create_conversation(
    session: Session,
    project_id: uuid.UUID,
) -> genesis_db.Conversation:
    """
    Start a new conversation for a project.

    A project may have multiple conversations over its lifecycle
    (initial discovery, change requests, repair discussions).

    Returns:
        Newly created Conversation in ACTIVE status.
    """
    conversation = genesis_db.Conversation(
        project_id=project_id,
        status=genesis_db.ConversationStatus.ACTIVE,
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    logger.info(
        "Conversation created",
        extra={
            "conversation_id": str(conversation.id),
            "project_id": str(project_id),
        },
    )
    return conversation


def get_conversation(
    session: Session,
    conversation_id: uuid.UUID,
    project_id: uuid.UUID,
) -> genesis_db.Conversation:
    """
    Retrieve a conversation, verifying it belongs to the given project.

    Raises:
        NotFoundError: If conversation not found or belongs to different project.
    """
    conversation = session.get(genesis_db.Conversation, conversation_id)
    if not conversation or conversation.project_id != project_id:
        raise NotFoundError(
            "Conversation not found.",
            code=ErrorCode.NOT_FOUND,
        )
    return conversation


def list_conversations(
    session: Session,
    project_id: uuid.UUID,
) -> list[genesis_db.Conversation]:
    """Return all conversations for a project, most recent first."""
    return list(
        session.exec(
            select(genesis_db.Conversation)
            .where(genesis_db.Conversation.project_id == project_id)
            .order_by(sa.col(genesis_db.Conversation.created_at).desc())
        ).all()
    )


def get_active_conversation(
    session: Session,
    project_id: uuid.UUID,
) -> genesis_db.Conversation | None:
    """Return the most recent active conversation for a project, or None."""
    return session.exec(
        select(genesis_db.Conversation)
        .where(
            genesis_db.Conversation.project_id == project_id,
            genesis_db.Conversation.status == genesis_db.ConversationStatus.ACTIVE,
        )
        .order_by(sa.col(genesis_db.Conversation.created_at).desc())
    ).first()


# =============================================================================
# Message management
# =============================================================================


def add_message(
    session: Session,
    conversation_id: uuid.UUID,
    *,
    role: str,
    content: str,
    message_type: str = genesis_db.MessageType.CHAT,
    metadata: dict | None = None,
) -> genesis_db.ConversationMessage:
    """
    Persist a single message to the conversation.

    Args:
        session: Database session.
        conversation_id: Target conversation.
        role: 'user' | 'assistant' | 'system' | 'agent'
        content: Full message content.
        message_type: Semantic type (chat, question, confirmation, etc.)
        metadata: Optional structured data (e.g., requirement IDs, approval state).
                  Must NOT contain PII or sensitive data.

    Returns:
        Persisted ConversationMessage.
    """
    message = genesis_db.ConversationMessage(
        conversation_id=conversation_id,
        role=role,
        content=content,
        message_type=message_type,
        metadata=metadata,
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    return message


def get_messages(
    session: Session,
    conversation_id: uuid.UUID,
    limit: int = 100,
    offset: int = 0,
) -> list[genesis_db.ConversationMessage]:
    """Return messages for a conversation, oldest first (chronological order)."""
    return list(
        session.exec(
            select(genesis_db.ConversationMessage)
            .where(genesis_db.ConversationMessage.conversation_id == conversation_id)
            .order_by(sa.col(genesis_db.ConversationMessage.created_at).asc())
            .limit(limit)
            .offset(offset)
        ).all()
    )


def build_llm_messages(
    messages: list[genesis_db.ConversationMessage],
    system_prompt: str,
) -> list[dict[str, str]]:
    """
    Convert DB conversation messages into LiteLLM message format.

    The system prompt is prepended as the first message.
    Agent and system messages are included as assistant context.

    Args:
        messages: Ordered conversation messages from DB.
        system_prompt: Prompt content from prompt_registry (NOT inline).

    Returns:
        List of {"role": str, "content": str} dicts for LiteLLM.
    """
    result: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

    for msg in messages:
        role = msg.role
        # Map agent/system messages to assistant role for LLM context
        if role in (genesis_db.MessageRole.AGENT, genesis_db.MessageRole.SYSTEM):
            role = "assistant"
        result.append({"role": role, "content": msg.content})

    return result


# =============================================================================
# Streaming response generation
# =============================================================================


async def generate_response_stream(
    session: Session,
    *,
    conversation: genesis_db.Conversation,
    user_message: str,
    user: genesis_db.User,
    model_registry_id: uuid.UUID,
) -> AsyncIterator[str]:
    """
    Process a user message and stream the AI response.

    Flow:
        1. Persist user message
        2. Retrieve conversation history
        3. Get system prompt from prompt_registry
        4. Create ai_run record (MANDATORY before LLM call)
        5. Stream LLM response tokens
        6. Persist complete assistant response
        7. Dispatch RequirementAgent to extract requirements (async via NATS)

    Yields:
        Response tokens as they arrive from the LLM.

    Note:
        This is an async generator — call with `async for token in generate_response_stream(...)`.
        The full response is persisted after the stream completes.
    """
    from services.agent_service import create_ai_run, update_ai_run_status
    from services.llm_service import get_active_prompt, stream_complete

    # 1. Persist user message
    add_message(
        session,
        conversation.id,
        role=genesis_db.MessageRole.USER,
        content=user_message,
        message_type=genesis_db.MessageType.CHAT,
    )

    # 2. Retrieve conversation history
    messages = get_messages(session, conversation.id)

    # 3. Get system prompt from registry (no inline prompts per AI_GOVERNANCE.md §3)
    prompt = get_active_prompt(session, "conversation_agent")
    system_prompt = prompt.content

    # 4. Build LLM message list
    llm_messages = build_llm_messages(messages, system_prompt)

    # 5. Create ai_run BEFORE calling LLM (mandatory)
    run = create_ai_run(
        session,
        run_type="conversation_response",
        project_id=conversation.project_id,
        triggered_by_user_id=user.id,
        input_summary={
            "conversation_id": str(conversation.id),
            "message_count": len(messages),
        },
    )

    # Update model_id on run now that we have it
    run.model_id = model_registry_id
    session.add(run)
    session.commit()

    # 6. Stream LLM response
    full_response_parts: list[str] = []

    async for token in stream_complete(
        session,
        model_registry_id,
        llm_messages,
        run,
    ):
        full_response_parts.append(token)
        yield token

    full_response = "".join(full_response_parts)

    # 7. Persist complete assistant response
    add_message(
        session,
        conversation.id,
        role=genesis_db.MessageRole.ASSISTANT,
        content=full_response,
        message_type=genesis_db.MessageType.CHAT,
        metadata={"ai_run_id": str(run.id)},
    )

    # 8. Mark run complete
    update_ai_run_status(
        session,
        run,
        genesis_db.AIRunStatus.COMPLETED,
        output_summary={"response_length": len(full_response)},
    )

    logger.info(
        "Conversation response complete",
        extra={
            "conversation_id": str(conversation.id),
            "run_id": str(run.id),
            "response_length": len(full_response),
        },
    )


# =============================================================================
# Requirement management
# =============================================================================


def list_requirements(
    session: Session,
    project_id: uuid.UUID,
) -> list[genesis_db.Requirement]:
    """Return all requirements for a project."""
    return list(
        session.exec(
            select(genesis_db.Requirement)
            .where(genesis_db.Requirement.project_id == project_id)
            .order_by(sa.col(genesis_db.Requirement.created_at).asc())
        ).all()
    )


def upsert_requirement(
    session: Session,
    project_id: uuid.UUID,
    requirement_key: str,
    *,
    title: str,
    description: str,
    category: str = genesis_db.RequirementCategory.FUNCTIONAL,
    priority: str = genesis_db.RequirementPriority.MEDIUM,
    confidence: float | None = None,
    source_message_id: uuid.UUID | None = None,
) -> genesis_db.Requirement:
    """
    Create or update a requirement for a project.

    If a requirement with the same requirement_key already exists for this project,
    it is updated. Otherwise a new one is created.

    Note: LLM-extracted requirement data must be validated against this function's
    parameters before being persisted (per AI_GOVERNANCE.md §6).
    """
    existing = session.exec(
        select(genesis_db.Requirement).where(
            genesis_db.Requirement.project_id == project_id,
            genesis_db.Requirement.requirement_key == requirement_key,
        )
    ).first()

    if existing:
        existing.title = title
        existing.description = description
        existing.category = category
        existing.priority = priority
        if confidence is not None:
            existing.confidence = confidence
        if source_message_id is not None:
            existing.source_message_id = source_message_id
        session.add(existing)
        session.commit()
        session.refresh(existing)
        return existing
    else:
        req = genesis_db.Requirement(
            project_id=project_id,
            requirement_key=requirement_key,
            title=title,
            description=description,
            category=category,
            priority=priority,
            confidence=confidence,
            source_message_id=source_message_id,
        )
        session.add(req)
        session.commit()
        session.refresh(req)
        logger.info(
            "Requirement created",
            extra={
                "requirement_id": str(req.id),
                "key": requirement_key,
                "project_id": str(project_id),
            },
        )
        return req
