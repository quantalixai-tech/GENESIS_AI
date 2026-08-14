"""
Database seed script for AI Governance tables.
Runs automatically after migrations via `genesis migrate`.
"""

import uuid

import bcrypt
from sqlmodel import Session, select

from genesis_db import engine
from genesis_db.governance import (
    AgentRegistry,
    AgentRiskLevel,
    ModelProvider,
    ModelRegistry,
    PromptRegistry,
    PromptStatus,
)
from genesis_db.models import User


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def seed_db():
    with Session(engine) as session:
        print("Seeding ModelRegistry...")
        existing_model = session.exec(
            select(ModelRegistry).where(ModelRegistry.model_id == "llama3.2:3b")
        ).first()
        if not existing_model:
            model = ModelRegistry(
                id=uuid.uuid4(),
                name="Llama 3.2 3B",
                model_id="llama3.2:3b",
                provider=ModelProvider.OLLAMA,
                version="1.0",
                is_active=True,
                context_window=8192,
                max_output_tokens=4096,
                description="Local Ollama llama3.2:3b model",
            )
            session.add(model)

        print("Seeding PromptRegistry...")
        existing_prompt = session.exec(
            select(PromptRegistry).where(PromptRegistry.prompt_key == "extract_requirements")
        ).first()
        if not existing_prompt:
            prompt = PromptRegistry(
                id=uuid.uuid4(),
                prompt_key="extract_requirements",
                title="Extract Requirements",
                version=1,
                content="""You are GENESIS AI, a senior software architect. Your goal is to extract structured software requirements from the user's description.
Analyze the user's input and reply as a JSON object strictly matching the following schema.
Do not wrap your response in markdown code blocks. Just output raw JSON.

Schema:
{
  "clarifying_questions": ["question 1", "question 2"],
  "extracted_requirements": [
    {
      "requirement_key": "REQ-1",
      "title": "Short title",
      "description": "Detailed description",
      "category": "feature|non-functional|security",
      "priority": "high|medium|low"
    }
  ]
}""",
                status=PromptStatus.ACTIVE,
            )
            session.add(prompt)

        print("Seeding AgentRegistry...")
        existing_agent = session.exec(
            select(AgentRegistry).where(AgentRegistry.agent_key == "requirement_agent")
        ).first()
        if not existing_agent:
            agent = AgentRegistry(
                id=uuid.uuid4(),
                agent_key="requirement_agent",
                name="RequirementAgent",
                agent_type="REQUIREMENT",
                purpose="Agent that extracts requirements from user conversations",
                risk_level=AgentRiskLevel.LOW,
                requires_approval=False,
                allowed_tools=[],
            )
            session.add(agent)

        existing_coding_agent = session.exec(
            select(AgentRegistry).where(AgentRegistry.agent_key == "coding_agent")
        ).first()
        if not existing_coding_agent:
            coding_agent = AgentRegistry(
                id=uuid.uuid4(),
                agent_key="coding_agent",
                name="CodingAgent",
                agent_type="CODING",
                purpose="Agent that generates and modifies source code",
                risk_level=AgentRiskLevel.MEDIUM,
                requires_approval=False,
                allowed_tools=["file_ops"],
            )
            session.add(coding_agent)

        print("Seeding Admin User...")
        existing_user = session.exec(select(User).where(User.email == "admin@genesis.ai")).first()
        if not existing_user:
            admin_user = User(
                id=uuid.uuid4(),
                email="admin@genesis.ai",
                hashed_password=get_password_hash("password123"),
            )
            session.add(admin_user)

        session.commit()
        print("Database seeded successfully!")


if __name__ == "__main__":
    seed_db()
