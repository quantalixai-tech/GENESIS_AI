"""
scripts/seed_admin.py — Seed the admin user.

Usage (run from apps/api/src/ so core.* imports resolve):
    cd apps/api/src
    uv run python ../../scripts/seed_admin.py

WARNING: Contains hardcoded dev credentials. Never run in production.
"""

from sqlmodel import Session, select

import genesis_db
from core.security import get_password_hash


def seed_admin() -> None:
    with Session(genesis_db.engine) as session:
        # Check if admin exists
        stmt = select(genesis_db.User).where(genesis_db.User.email == "admin@genesis.ai")
        admin = session.exec(stmt).first()
        if admin:
            print("Admin already exists, updating password.")
            admin.hashed_password = get_password_hash("Admin123!")
            session.add(admin)
            session.commit()
            print("Admin updated: admin@genesis.ai / Admin123!")
            return

        # Create admin
        admin = genesis_db.User(
            email="admin@genesis.ai",
            hashed_password=get_password_hash("Admin123!"),
            is_active=True,
            is_superuser=True,
            full_name="System Administrator",
        )
        session.add(admin)
        session.commit()
        print("Admin created: admin@genesis.ai / Admin123!")


if __name__ == "__main__":
    seed_admin()
