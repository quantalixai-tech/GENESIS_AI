import abc
import uuid
import time
from typing import Any, Dict, Optional
from pydantic import BaseModel
from sqlmodel import Session
from datetime import datetime, UTC

import genesis_db
from core.logging import get_logger

logger = get_logger(__name__)

class AgentContext(BaseModel):
    session: Any  # sqlmodel Session (not strongly typed here to avoid pydantic issues)
    project_id: Optional[uuid.UUID] = None
    triggered_by_user_id: Optional[uuid.UUID] = None
    run_id: Optional[uuid.UUID] = None
    parent_run_id: Optional[uuid.UUID] = None

class AgentResult(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    usage_stats: Optional[Dict[str, Any]] = None

class BaseAgent(abc.ABC):
    """
    Base class for all Genesis agents.
    Enforces AI governance (AIRun tracking) and standardized execution.
    """
    
    agent_key: str
    
    def __init__(self, agent_record: genesis_db.AgentRegistry):
        self.agent_record = agent_record
        
    @abc.abstractmethod
    async def _execute(self, context: AgentContext, input_data: Dict[str, Any]) -> AgentResult:
        """
        The actual agent logic. Must be implemented by subclasses.
        """
        pass

    async def execute(self, context: AgentContext, input_data: Dict[str, Any]) -> AgentResult:
        """
        Wrapper that handles AI Governance (AIRun creation/completion) and error handling.
        """
        session = context.session
        
        # 1. Create AIRun record (PENDING)
        run = genesis_db.AIRun(
            run_type=self.agent_record.agent_type,
            status=genesis_db.AIRunStatus.PENDING,
            project_id=context.project_id,
            agent_id=self.agent_record.id,
            triggered_by_user_id=context.triggered_by_user_id,
            parent_run_id=context.parent_run_id,
            input_summary=input_data,  # Store a summary, not PII
            started_at=datetime.now(UTC)
        )
        session.add(run)
        session.commit()
        session.refresh(run)
        
        context.run_id = run.id
        logger.info(f"[{self.agent_key}] Started execution", extra={"run_id": str(run.id)})
        
        start_time = time.time()
        
        try:
            # 2. Execute agent logic
            run.status = genesis_db.AIRunStatus.RUNNING
            session.add(run)
            session.commit()
            
            result = await self._execute(context, input_data)
            
            # 3. Update AIRun record (COMPLETED / FAILED)
            duration_ms = int((time.time() - start_time) * 1000)
            
            if result.success:
                run.status = genesis_db.AIRunStatus.COMPLETED
                run.output_summary = result.data
                
                if result.usage_stats:
                    run.prompt_tokens = result.usage_stats.get("prompt_tokens")
                    run.completion_tokens = result.usage_stats.get("completion_tokens")
                    run.total_tokens = result.usage_stats.get("total_tokens")
                    
            else:
                run.status = genesis_db.AIRunStatus.FAILED
                run.error_message = result.error
                
            run.duration_ms = duration_ms
            run.completed_at = datetime.now(UTC)
            
            session.add(run)
            session.commit()
            
            logger.info(f"[{self.agent_key}] Completed execution", extra={"success": result.success, "duration_ms": duration_ms})
            return result
            
        except Exception as e:
            logger.exception(f"[{self.agent_key}] Unhandled exception during execution")
            
            run.status = genesis_db.AIRunStatus.FAILED
            run.error_message = str(e)
            run.duration_ms = int((time.time() - start_time) * 1000)
            run.completed_at = datetime.now(UTC)
            
            session.add(run)
            session.commit()
            
            return AgentResult(success=False, error=str(e))
