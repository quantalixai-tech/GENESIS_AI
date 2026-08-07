import os
from sqlmodel import create_engine, SQLModel, Session

# By default, try to connect to the docker postgres instance, but allow override
# E.g. "postgresql://genesis:genesis@localhost:5432/genesis"
DATABASE_URL = os.environ.get(
    "DATABASE_URL", 
    "postgresql://genesis:genesis@localhost:5432/genesis"
)

# Set echo=True for debugging if needed
engine = create_engine(DATABASE_URL, echo=False)

def get_session():
    with Session(engine) as session:
        yield session

# Note: We use Alembic for migrations, but this is a helper to create tables directly for testing
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
