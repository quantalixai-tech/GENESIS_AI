from typing import Any, Dict, List
from pydantic import BaseModel, Field
import genesis_db
from sqlmodel import select

from ..base import BaseAgent, AgentContext, AgentResult
from ..ai_service import generate_completion
from core.logging import get_logger

logger = get_logger(__name__)

class ExtractedRequirement(BaseModel):
    requirement_key: str = Field(description="Unique ID e.g. REQ-1")
    title: str = Field(description="Short title")
    description: str = Field(description="Detailed description")
    category: str = Field(description="feature|non-functional|security")
    priority: str = Field(description="high|medium|low")

class RequirementAgentOutput(BaseModel):
    clarifying_questions: List[str] = Field(default_factory=list)
    extracted_requirements: List[ExtractedRequirement] = Field(default_factory=list)

class RequirementAgent(BaseAgent):
    agent_key = "requirement_agent"
    
    async def _execute(self, context: AgentContext, input_data: Dict[str, Any]) -> AgentResult:
        user_input = input_data.get("user_input", "")
        if not user_input:
            return AgentResult(success=False, error="Missing 'user_input' in Agent input_data")
            
        # Get the system prompt
        prompt_record = context.session.exec(
            select(genesis_db.PromptRegistry).where(
                genesis_db.PromptRegistry.prompt_key == "extract_requirements"
            )
        ).first()
        
        system_prompt = prompt_record.content if prompt_record else "Extract requirements from the input as JSON."
        
        # Get model ID (fallback to llama3.2:3b if not specified on the agent)
        model_name = "llama3.2:3b"
        if self.agent_record.model_id:
            model_record = context.session.get(genesis_db.ModelRegistry, self.agent_record.model_id)
            if model_record:
                model_name = model_record.model_id
                
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        try:
            parsed_data, usage_stats = await generate_completion(
                model=model_name,
                messages=messages,
                response_schema=RequirementAgentOutput
            )
            
            return AgentResult(
                success=True,
                data=parsed_data.model_dump(),
                usage_stats=usage_stats
            )
            
        except Exception as e:
            logger.error(f"Failed to generate requirements: {e}")
            return AgentResult(success=False, error=str(e))
