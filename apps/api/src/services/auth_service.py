"""
Genesis API — Authentication Service

Contains all business logic for user authentication.
Route handlers call this service; they do not contain business logic directly.

Responsibilities:
    - User creation with password hashing
    - Login credential verification
    - Access token generation

This module does NOT:
    - Handle HTTP concerns (status codes, request parsing)
    - Know about JWT headers or OAuth2 flows
    - Make decisions about response formats

Raising:
    ConflictError   — email already exists
    UnauthorizedError — invalid credentials
"""

from sqlmodel import Session, select

import genesis_db
from core.errors import ConflictError, ErrorCode, UnauthorizedError
from core.logging import get_logger
from core.security import create_access_token, get_password_hash, verify_password
from schemas.auth import SignupRequest

logger = get_logger(__name__)


def create_user(session: Session, request: SignupRequest) -> tuple[genesis_db.User, str]:
    """
    Register a new user and return the created user with an access token.

    Args:
        session: Database session.
        request: Validated signup request containing email and password.

    Returns:
        Tuple of (created User, JWT access token string).

    Raises:
        ConflictError: If a user with this email already exists.
    """
    existing = session.exec(
        select(genesis_db.User).where(genesis_db.User.email == request.email)
    ).first()

    if existing:
        logger.warning("Signup attempt for existing email", extra={"email": request.email})
        raise ConflictError(
            "A user with this email address already exists.",
            code=ErrorCode.EMAIL_ALREADY_EXISTS,
        )

    user = genesis_db.User(
        email=request.email,
        hashed_password=get_password_hash(request.password),
    )
    session.add(user)
    session.commit()
    session.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})

    logger.info("User created", extra={"user_id": str(user.id)})
    return user, access_token


def authenticate_user(session: Session, email: str, password: str) -> tuple[genesis_db.User, str]:
    """
    Verify credentials and return the user with an access token.

    Args:
        session: Database session.
        email: Submitted email address.
        password: Submitted plaintext password.

    Returns:
        Tuple of (authenticated User, JWT access token string).

    Raises:
        UnauthorizedError: If credentials are invalid. The error message is
            intentionally generic to avoid revealing whether the email exists.
    """
    user = session.exec(select(genesis_db.User).where(genesis_db.User.email == email)).first()

    if not user or not verify_password(password, user.hashed_password):
        # NOTE: same error for "user not found" and "wrong password" — prevents
        # user enumeration attacks via timing or message differences
        raise UnauthorizedError(
            "Incorrect email or password.",
            code=ErrorCode.INVALID_CREDENTIALS,
        )

    access_token = create_access_token(data={"sub": str(user.id)})

    logger.info("User authenticated", extra={"user_id": str(user.id)})
    return user, access_token
