from typing import Type, Dict, Optional
import genesis_db
from sqlmodel import Session, select
from .base import BaseAgent

class AgentRegistryError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

class AgentRegistryService:
    """
    In-memory registry mapping Agent Keys (from DB) to Python implementations.
    """
    def __init__(self):
        self._agents: Dict[str, Type[BaseAgent]] = {}
        
    def register(self, agent_key: str, agent_class: Type[BaseAgent]):
        """Register a Python agent class for a given agent_key."""
        self._agents[agent_key] = agent_class
        
    def get_agent(self, session: Session, agent_key: str) -> BaseAgent:
        """
        Instantiate an agent by key.
        Validates that the agent exists in the DB (AgentRegistry) before instantiating.
        """
        agent_class = self._agents.get(agent_key)
        if not agent_class:
            raise AgentRegistryError(f"No implementation registered for agent '{agent_key}'")
            
        agent_record = session.exec(
            select(genesis_db.AgentRegistry).where(genesis_db.AgentRegistry.agent_key == agent_key)
        ).first()
        
        if not agent_record:
            raise AgentRegistryError(f"Agent '{agent_key}' not found in database AgentRegistry")
            
        if not agent_record.is_active:
            raise AgentRegistryError(f"Agent '{agent_key}' is disabled")
            
        return agent_class(agent_record)

# Singleton registry
_registry = AgentRegistryService()

def get_agent_registry() -> AgentRegistryService:
    return _registry
