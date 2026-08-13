"""
Genesis API — Conversation Routes

Handles HTTP for the conversation domain.
All business logic delegates to conversation_service.

Routes:
    POST   /api/v1/projects/{project_id}/conversations
    GET    /api/v1/projects/{project_id}/conversations
    POST   /api/v1/projects/{project_id}/conversations/{conversation_id}/messages
    GET    /api/v1/projects/{project_id}/conversations/{conversation_id}/messages
    GET    /api/v1/projects/{project_id}/conversations/{conversation_id}/stream  (SSE)
    GET    /api/v1/projects/{project_id}/requirements
"""

import json
import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlmodel import Session

import genesis_db
from core.database import get_session
from core.security import get_current_user
from services import conversation_service, llm_service

router = APIRouter(prefix="/projects/{project_id}/conversations", tags=["conversations"])


# =============================================================================
# Schemas (inline for conversation domain — simple enough to not need own file)
# =============================================================================


class ConversationResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: uuid.UUID
    conversation_id: uuid.UUID
    role: str
    content: str
    message_type: str
    metadata: dict | None
    created_at: datetime

    model_config = {"from_attributes": True}


class SendMessageRequest(BaseModel):
    content: str


class RequirementResponse(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    requirement_key: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    confidence: float | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# Dependencies
# =============================================================================


def _get_db() -> Session:  # pragma: no cover
    return next(get_session())


SessionDep = Annotated[Session, Depends(_get_db)]
CurrentUser = Annotated[genesis_db.User, Depends(get_current_user)]


def _resolve_project(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> genesis_db.Project:
    """Resolve project and verify ownership."""
    from services.project_service import _get_workspace_for_user

    project = session.get(genesis_db.Project, project_id)
    if not project:
        from core.errors import ErrorCode, NotFoundError

        raise NotFoundError("Project not found.", code=ErrorCode.PROJECT_NOT_FOUND)

    # Verify user owns the workspace containing this project
    _get_workspace_for_user(session, project.workspace_id, current_user)
    return project


# =============================================================================
# Routes
# =============================================================================


@router.post(
    "",
    response_model=ConversationResponse,
    status_code=201,
    summary="Start a new conversation for a project",
)
async def create_conversation(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> genesis_db.Conversation:
    """Start a new AI conversation for a project."""
    _resolve_project(project_id, session, current_user)
    return conversation_service.create_conversation(session, project_id)


@router.get(
    "",
    response_model=list[ConversationResponse],
    summary="List all conversations for a project",
)
async def list_conversations(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> list[genesis_db.Conversation]:
    """Return all conversations for a project."""
    _resolve_project(project_id, session, current_user)
    return conversation_service.list_conversations(session, project_id)


@router.post(
    "/{conversation_id}/messages",
    response_model=MessageResponse,
    status_code=201,
    summary="Send a message to a conversation",
)
async def send_message(
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
    request: SendMessageRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> genesis_db.ConversationMessage:
    """Persist a user message. Use the /stream endpoint to also get the AI response."""
    _resolve_project(project_id, session, current_user)
    conversation = conversation_service.get_conversation(session, conversation_id, project_id)

    return conversation_service.add_message(
        session,
        conversation.id,
        role=genesis_db.MessageRole.USER,
        content=request.content,
    )


@router.get(
    "/{conversation_id}/messages",
    response_model=list[MessageResponse],
    summary="Get conversation message history",
)
async def get_messages(
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = 100,
    offset: int = 0,
) -> list[genesis_db.ConversationMessage]:
    """Return messages for a conversation in chronological order."""
    _resolve_project(project_id, session, current_user)
    conversation_service.get_conversation(session, conversation_id, project_id)
    return conversation_service.get_messages(session, conversation_id, limit=limit, offset=offset)


@router.get(
    "/{conversation_id}/stream",
    summary="Stream AI response for a user message (SSE)",
    response_class=StreamingResponse,
)
async def stream_response(
    project_id: uuid.UUID,
    conversation_id: uuid.UUID,
    message: str,
    session: SessionDep,
    current_user: CurrentUser,
) -> StreamingResponse:
    """
    Stream the AI response for a user message via Server-Sent Events (SSE).

    Per ADR-008 — unidirectional SSE for LLM token streaming.

    Query params:
        message: The user's message content.

    SSE event format:
        data: {"type": "token", "content": "<token>"}
        data: {"type": "done"}
        data: {"type": "error", "message": "<error>"}
    """
    _resolve_project(project_id, session, current_user)
    conversation = conversation_service.get_conversation(session, conversation_id, project_id)

    # Get default model for this project
    model = llm_service.get_default_model(session)

    async def event_generator():  # type: ignore[return]
        try:
            async for token in conversation_service.generate_response_stream(
                session,
                conversation=conversation,
                user_message=message,
                user=current_user,
                model_registry_id=model.id,
            ):
                yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        except Exception as exc:
            yield f"data: {json.dumps({'type': 'error', 'message': str(exc)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# =============================================================================
# Requirements (separate prefix but logically part of conversation domain)
# =============================================================================

requirements_router = APIRouter(
    prefix="/projects/{project_id}/requirements",
    tags=["requirements"],
)


@requirements_router.get(
    "",
    response_model=list[RequirementResponse],
    summary="List all requirements for a project",
)
async def list_requirements(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> list[genesis_db.Requirement]:
    """Return all requirements extracted from the project conversation."""
    _resolve_project(project_id, session, current_user)
    return conversation_service.list_requirements(session, project_id)
