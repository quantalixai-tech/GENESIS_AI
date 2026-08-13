import uuid
from sqlmodel import Session
from services.governance_service import create_ai_run, complete_ai_run
import genesis_db

def test_governance():
    with Session(genesis_db.engine) as session:
        # Check if any model exists (we might not have seeded models yet)
        # We can just create an AIRun without foreign keys if they are nullable
        run = create_ai_run(
            session=session,
            run_type="test_run",
            input_summary={"prompt": "hello world"}
        )
        print("Created AIRun:", run.id)
        
        # Complete it
        completed_run = complete_ai_run(
            session=session,
            run_id=run.id,
            output_summary={"response": "hello back"},
            usage_stats={"duration_ms": 100, "total_tokens": 50}
        )
        print("Completed AIRun. Duration:", completed_run.duration_ms)

if __name__ == "__main__":
    test_governance()
