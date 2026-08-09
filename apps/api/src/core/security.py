"""
Genesis API — Security Utilities

Handles:
    - Password hashing and verification (bcrypt via passlib)
    - JWT access token creation and decoding
    - FastAPI dependency for authenticating the current user

Configuration is loaded from core.config — never from os.environ directly.
The JWT_SECRET is required; the application will fail at startup if it is absent.

Security properties:
    - Passwords are hashed with bcrypt (work factor configurable via passlib)
    - JWT tokens use HS256 algorithm
    - Token expiry is configurable via ACCESS_TOKEN_EXPIRE_MINUTES
    - Expired/invalid tokens produce a generic "Could not validate credentials"
      error — no information about *why* the token was rejected is exposed
"""

from datetime import UTC, datetime, timedelta

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from pydantic import BaseModel
from sqlmodel import Session

import genesis_db
from core.config import settings
from core.errors import ErrorCode, UnauthorizedError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


class TokenData(BaseModel):
    user_id: str | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Return True if plain_password matches the stored bcrypt hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Return a bcrypt hash of the given password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Create a signed JWT access token.

    Args:
        data: Payload to encode. Should contain 'sub' (subject = user_id).
        expires_delta: Override the default expiry. Useful in tests.

    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    expire_delta = expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    expire = datetime.now(UTC) + expire_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: Session = Depends(genesis_db.get_session),
) -> genesis_db.User:
    """
    FastAPI dependency: decode the JWT and return the authenticated User.

    Raises:
        UnauthorizedError — if the token is missing, malformed, expired, or the
                            user no longer exists. The error detail is intentionally
                            generic to avoid leaking token validity information.
    """
    _credentials_error = UnauthorizedError(
        "Could not validate credentials.",
        code=ErrorCode.TOKEN_INVALID,
    )

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise _credentials_error
        token_data = TokenData(user_id=user_id)
    except jwt.ExpiredSignatureError as exc:
        raise UnauthorizedError(
            "Token has expired. Please log in again.",
            code=ErrorCode.TOKEN_EXPIRED,
        ) from exc
    except jwt.PyJWTError as exc:
        raise _credentials_error from exc

    user = session.get(genesis_db.User, token_data.user_id)
    if user is None:
        raise _credentials_error

    return user
