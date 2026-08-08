"""
Genesis API — Authentication Schemas

These are the API-layer request/response schemas for authentication endpoints.
They are separate from the database models in genesis_db to decouple
the API contract from the database schema.

Rules:
    - Never include hashed_password in any response schema
    - UserResponse must not expose internal DB fields (e.g., updated_at if internal)
    - Request schemas validate user input before it reaches service code
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class SignupRequest(BaseModel):
    """Request body for POST /api/v1/auth/signup"""

    email: EmailStr = Field(
        description="User email address. Must be a valid email format.",
        examples=["user@example.com"],
    )
    password: str = Field(
        min_length=8,
        max_length=128,
        description="Password. Minimum 8 characters.",
    )

    @field_validator("password")
    @classmethod
    def password_not_whitespace_only(cls, v: str) -> str:
        if v.strip() == "":
            raise ValueError("Password must not be whitespace only.")
        return v


class LoginResponse(BaseModel):
    """Response body for POST /api/v1/auth/login and /signup"""

    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


class UserResponse(BaseModel):
    """
    Public user representation returned in API responses.

    Deliberately omits:
        - hashed_password
        - Any future internal flags
    """

    id: uuid.UUID
    email: str
    created_at: datetime

    model_config = {"from_attributes": True}


class MeResponse(UserResponse):
    """Response body for GET /api/v1/auth/me — same as UserResponse for now."""

    pass
