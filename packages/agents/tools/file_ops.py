import hashlib
import os
import uuid
from pathlib import Path

from pydantic import BaseModel, Field
from sqlmodel import Session, select

from core.logging import get_logger
from genesis_db.execution_models import ProjectFile, FileStatus

logger = get_logger(__name__)

class FileOperation(BaseModel):
    action: str = Field(description="'create', 'modify', or 'delete'")
    path: str = Field(description="Project-relative path (e.g., 'src/main.py')")
    content: str | None = Field(default=None, description="File content (for create/modify)")


def compute_hash(content: str) -> str:
    """Compute SHA-256 hash of string content."""
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def apply_file_operations(
    session: Session,
    project_id: uuid.UUID,
    project_repo_path: str,
    operations: list[FileOperation]
) -> None:
    """
    Applies file operations to the disk and updates the ProjectFile records in the DB.
    """
    base_path = Path(project_repo_path)
    if not base_path.exists():
        logger.warning(f"Project repo path {base_path} does not exist. Creating it.")
        base_path.mkdir(parents=True, exist_ok=True)

    for op in operations:
        full_path = base_path / op.path
        
        # Ensure path is within base_path to prevent path traversal
        try:
            full_path.resolve().relative_to(base_path.resolve())
        except ValueError:
            logger.error(f"Path traversal detected: {op.path}")
            continue

        existing_file = session.exec(
            select(ProjectFile).where(
                ProjectFile.project_id == project_id,
                ProjectFile.path == op.path
            )
        ).first()

        if op.action == "delete":
            if full_path.exists():
                if full_path.is_file():
                    full_path.unlink()
                else:
                    logger.error(f"Cannot delete directory yet: {full_path}")
            
            if existing_file:
                existing_file.status = FileStatus.DELETED
                session.add(existing_file)

        elif op.action in ["create", "modify"]:
            if op.content is None:
                logger.error(f"Content is required for action {op.action} on {op.path}")
                continue
                
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write to disk
            full_path.write_text(op.content, encoding="utf-8")
            
            # Update or create DB record
            file_hash = compute_hash(op.content)
            
            if existing_file:
                existing_file.content_hash = file_hash
                existing_file.size_bytes = len(op.content.encode("utf-8"))
                existing_file.status = FileStatus.MODIFIED
                session.add(existing_file)
            else:
                new_file = ProjectFile(
                    project_id=project_id,
                    path=op.path,
                    file_type="file",
                    content_hash=file_hash,
                    size_bytes=len(op.content.encode("utf-8")),
                    status=FileStatus.TRACKED
                )
                session.add(new_file)
                
    # Commit changes to DB
    session.commit()
    logger.info(f"Applied {len(operations)} file operations for project {project_id}")
