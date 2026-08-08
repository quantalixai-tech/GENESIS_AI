"""
Genesis Database — Connection and Session Management

Database connectivity for the Genesis platform.

Configuration is read from the DATABASE_URL environment variable.
Default: postgresql://genesis:genesis@localhost:5432/genesis

IMPORTANT:
    This module does NOT create tables. Tables are managed exclusively by Alembic
    migrations. Never call create_db_and_tables() in production code — it exists
    only as a testing utility and is clearly marked as such.

    Run migrations with:
        cd packages/db && alembic upgrade head

Session usage:
    # In FastAPI route handlers:
    session: Session = Depends(genesis_db.get_session)

    # In scripts or tests:
    with Session(genesis_db.engine) as session:
        ...
"""

import os

from sqlmodel import Session, create_engine

# DATABASE_URL is the canonical way to configure the connection.
# In Docker Compose, this is injected via the environment.
# For local development outside Docker, set it in .env or .env.development.
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://genesis:genesis@localhost:5432/genesis",
)

engine = create_engine(
    DATABASE_URL,
    # Set pool_pre_ping=True so stale connections are detected and recycled
    # before they are handed to application code.
    pool_pre_ping=True,
    echo=False,  # Set to True only for debugging — very verbose
)


def get_session():
    """
    FastAPI dependency that provides a database session per request.

    Usage:
        session: Session = Depends(genesis_db.get_session)
    """
    with Session(engine) as session:
        yield session


# ---------------------------------------------------------------------------
# TEST UTILITY ONLY — never call in production or migration code
# ---------------------------------------------------------------------------

def create_db_and_tables_for_tests() -> None:
    """
    Create all tables directly from SQLModel metadata.

    WARNING: This bypasses Alembic migrations and should ONLY be used in
    unit tests that run against an in-memory or ephemeral database.
    Production schema is exclusively managed by Alembic.

    Example test usage:
        from sqlmodel import SQLModel
        engine = create_engine("sqlite:///:memory:")
        genesis_db.create_db_and_tables_for_tests()
    """
    from sqlmodel import SQLModel
    SQLModel.metadata.create_all(engine)
