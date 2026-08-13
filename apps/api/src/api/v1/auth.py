"""
Genesis API — Authentication Routes (v1)

Thin route handlers that delegate all business logic to auth_service.
Routes are responsible for:
    - Parsing and validating HTTP request bodies (via Pydantic schemas)
    - Calling the appropriate service function
    - Converting service results to HTTP responses
    - NOT containing any business logic
"""

from fastapi import APIRouter, Depends, Response
from pydantic import BaseModel
from sqlmodel import Session

import genesis_db
from core.security import get_current_user
from schemas.auth import LoginResponse, MeResponse, SignupRequest, UserResponse
from services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=LoginResponse,
    status_code=201,
    summary="Register a new user",
)
def signup(
    request: SignupRequest,
    response: Response,
    session: Session = Depends(genesis_db.get_session),
) -> LoginResponse:
    """
    Register a new user account.

    - Email must be a valid format and not already registered
    - Password must be at least 8 characters
    - Returns a JWT access token on success and sets HttpOnly cookie
    """
    user, token = auth_service.create_user(session, request)
    
    response.set_cookie(
        key="genesis_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False, # Set to True in production based on environment
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    
    return LoginResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


class LoginRequest(BaseModel):
    email: str
    password: str

@router.post(
    "/login",
    response_model=LoginResponse,
    summary="Authenticate and receive a JWT token",
)
def login(
    request: LoginRequest,
    response: Response,
    session: Session = Depends(genesis_db.get_session),
) -> LoginResponse:
    """
    Authenticate with email and password, returning a JWT access token.

    Accepts JSON body with email and password.
    Sets an HttpOnly cookie with the token.
    """
    user, token = auth_service.authenticate_user(
        session, email=request.email, password=request.password
    )
    
    response.set_cookie(
        key="genesis_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=60 * 60 * 24 * 7,
        path="/",
    )
    
    return LoginResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )

@router.post(
    "/logout",
    status_code=204,
    summary="Log out the current user",
)
def logout(response: Response) -> None:
    """Log out by clearing the genesis_token cookie."""
    response.delete_cookie("genesis_token", path="/")



@router.get(
    "/me",
    response_model=MeResponse,
    summary="Return the currently authenticated user",
)
def get_me(current_user: genesis_db.User = Depends(get_current_user)) -> MeResponse:
    """Return the profile of the currently authenticated user."""
    return MeResponse.model_validate(current_user)
