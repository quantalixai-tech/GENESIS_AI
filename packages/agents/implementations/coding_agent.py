import json
from typing import Any

from pydantic import BaseModel, Field

from agents.ai_service import generate_completion
from agents.base import AgentContext, BaseAgent, AgentResult
from agents.tools.file_ops import apply_file_operations, FileOperation
from core.logging import get_logger

logger = get_logger(__name__)


class CodingAgentOutput(BaseModel):
    operations: list[FileOperation] = Field(
        description="List of file operations to perform to fulfill the task"
    )
    summary: str = Field(
        description="A brief summary of the code generation changes made"
    )


class CodingAgent(BaseAgent):
    """
    An agent responsible for writing and modifying source code files.
    
    It accepts technical requirements and implementation task descriptions,
    generates the appropriate code, and applies the changes to the project's
    local repository via file_ops.
    """

    agent_key = "coding_agent"

    @property
    def agent_id(self) -> str:
        # In a real system, this would be a constant UUID looked up from the agent_registry table
        return "c0d1n900-0000-4000-8000-000000000000"

    @property
    def model_name(self) -> str:
        # Use llama3.2:3b as it's seeded in the database
        return "llama3.2:3b"

    async def _execute(self, context: AgentContext, input_data: dict[str, Any]) -> AgentResult:
        """
        Executes the coding task.
        """
        task_title = input_data.get("title", "Code Generation Task")
        task_description = input_data.get("description", "")
        task_context = input_data.get("context", {})
        project_repo_path = input_data.get("repository_path")
        
        if not project_repo_path:
            logger.error("Missing repository_path in input_data")
            return AgentResult(success=False, error="Missing repository_path")

        prompt = (
            f"You are an expert software developer. Your task is to implement the following:\n\n"
            f"Task: {task_title}\n"
            f"Description: {task_description}\n\n"
            f"Context: {json.dumps(task_context, indent=2)}\n\n"
            "Return a structured JSON output with a list of file operations (create, modify, delete) "
            "and the complete file contents to fulfill this task."
        )

        logger.info(f"Generating code for task: {task_title}")
        
        try:
            # 1. Generate code using LLM
            structured_response, usage_stats = await generate_completion(
                model=self.model_name,
                messages=[{"role": "user", "content": prompt}],
                response_schema=CodingAgentOutput,
            )
            
            logger.info(f"Code generated. Applying {len(structured_response.operations)} operations.")

            # 2. Apply file operations
            apply_file_operations(
                session=context.session,
                project_id=context.project_id,
                project_repo_path=project_repo_path,
                operations=structured_response.operations,
            )

            return AgentResult(
                success=True,
                data={
                    "summary": structured_response.summary,
                    "operations_count": len(structured_response.operations),
                },
                usage_stats=usage_stats
            )
        except Exception as e:
            logger.exception("Error during code generation")
            return AgentResult(success=False, error=str(e))
