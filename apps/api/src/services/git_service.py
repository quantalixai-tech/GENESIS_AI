"""
Genesis API — Git Service

Manages per-project git repositories using gitpython.

Architecture (per ADR-009):
    - Each project has a git repo at /projects/<project_id>/
    - Repos are on the genesis-projects named Docker volume
    - All git operations use gitpython (no subprocess calls)
    - Every commit writes a GitCommit DB record for fast history queries

Responsibilities:
    - Initialize project git repo on project creation
    - Stage and commit file changes with structured metadata
    - Query git history from DB (fast) and filesystem (detailed)
    - Restore previous project state from a commit
    - Generate diffs between commits

This module does NOT:
    - Generate code content (that is agent responsibility)
    - Handle HTTP concerns
    - Store secrets in commit messages or metadata

Raises:
    GenesisError — git operation failed
    NotFoundError — commit or repo not found
"""

import uuid
from pathlib import Path

import sqlalchemy as sa
from git import GitCommandError, InvalidGitRepositoryError, Repo
from sqlmodel import Session, select

import genesis_db
from core.config import settings
from core.errors import ErrorCode, GenesisError, NotFoundError
from core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# Project repository path
# =============================================================================

_PROJECTS_ROOT = Path(settings.projects_root)


def _project_repo_path(project_id: uuid.UUID) -> Path:
    """Return the filesystem path for a project's git repository."""
    return _PROJECTS_ROOT / str(project_id)


# =============================================================================
# Repository initialization
# =============================================================================


def initialize_project_repo(
    session: Session,
    project: genesis_db.Project,
) -> str:
    """
    Initialize a git repository for a newly created project.

    Creates the directory at /projects/<project_id>/ and runs git init.
    Updates project.repository_path in the DB.

    Args:
        session: Database session.
        project: Project record (must be newly created).

    Returns:
        Absolute path to the repository as a string.

    Raises:
        GenesisError: If repo initialization fails.
    """
    repo_path = _project_repo_path(project.id)
    repo_path.mkdir(parents=True, exist_ok=True)

    try:
        repo = Repo.init(str(repo_path))
        # Set default author identity for AI commits
        repo.config_writer().set_value("user", "name", "GENESIS AI").release()
        repo.config_writer().set_value("user", "email", "genesis-ai@platform.internal").release()
    except Exception as exc:
        raise GenesisError(
            f"Failed to initialize git repository: {exc!s}",
            code=ErrorCode.INTERNAL_ERROR,
        ) from exc

    # Persist repository path to project record
    project.repository_path = str(repo_path)
    session.add(project)
    session.commit()
    session.refresh(project)

    logger.info(
        "Git repository initialized",
        extra={
            "project_id": str(project.id),
            "path": str(repo_path),
        },
    )
    return str(repo_path)


# =============================================================================
# Commit operations
# =============================================================================


def _get_repo(project: genesis_db.Project) -> Repo:
    """
    Return the gitpython Repo for a project.

    Raises:
        NotFoundError: If repository_path not set or repo doesn't exist.
        GenesisError: If git repo is invalid.
    """
    if not project.repository_path:
        raise NotFoundError(
            f"Project {project.id} has no git repository. Call initialize_project_repo first.",
            code=ErrorCode.NOT_FOUND,
        )

    try:
        return Repo(project.repository_path)
    except InvalidGitRepositoryError as exc:
        raise GenesisError(
            f"Invalid git repository at {project.repository_path}",
            code=ErrorCode.INTERNAL_ERROR,
        ) from exc


def commit_changes(
    session: Session,
    project: genesis_db.Project,
    *,
    message: str,
    file_paths: list[str],
    author_type: str = genesis_db.GitAuthorType.AI,
    task_id: uuid.UUID | None = None,
    requirement_ids: list[str] | None = None,
) -> genesis_db.GitCommit:
    """
    Stage and commit changed files to the project git repository.

    Writes a GitCommit DB record for fast history queries.
    Commit message format:
        genesis(agent): <message>

        Task: TASK-001
        Requirements: REQ-001, REQ-002
        AI-Run: <ai_run_id>

    Args:
        session: Database session.
        project: Project record with repository_path set.
        message: Human-readable description of the change.
        file_paths: Project-relative file paths to stage and commit.
        author_type: 'user' | 'ai' | 'system'
        task_id: ImplementationTask that produced this change.
        requirement_ids: Requirement UUIDs addressed by this change.

    Returns:
        GitCommit DB record.

    Raises:
        GenesisError: If commit fails.
        NotFoundError: If repository not initialized.
    """
    repo = _get_repo(project)

    # Stage files
    try:
        repo.index.add(file_paths)
    except GitCommandError as exc:
        raise GenesisError(
            f"Failed to stage files: {exc!s}",
            code=ErrorCode.INTERNAL_ERROR,
        ) from exc

    # Build structured commit message
    full_message_parts = [f"genesis(agent): {message}", ""]
    if task_id:
        full_message_parts.append(f"Task: {task_id}")
    if requirement_ids:
        full_message_parts.append(f"Requirements: {', '.join(requirement_ids)}")
    full_message = "\n".join(full_message_parts).strip()

    # Commit
    try:
        commit = repo.index.commit(full_message)
    except GitCommandError as exc:
        raise GenesisError(
            f"Git commit failed: {exc!s}",
            code=ErrorCode.INTERNAL_ERROR,
        ) from exc

    # Write GitCommit DB record
    parent_hash: str | None = None
    if commit.parents:
        parent_hash = commit.parents[0].hexsha

    git_commit = genesis_db.GitCommit(
        project_id=project.id,
        commit_hash=commit.hexsha,
        message=full_message,
        parent_commit_hash=parent_hash,
        author_type=author_type,
        task_id=task_id,
        requirement_ids=requirement_ids,
        files_changed=file_paths,
    )
    session.add(git_commit)

    # Update project.current_commit_id
    project.current_commit_id = git_commit.id
    session.add(project)

    session.commit()
    session.refresh(git_commit)

    logger.info(
        "Git commit created",
        extra={
            "project_id": str(project.id),
            "commit_hash": commit.hexsha[:8],
            "files_changed": len(file_paths),
            "task_id": str(task_id) if task_id else None,
        },
    )
    return git_commit


# =============================================================================
# History and diff
# =============================================================================


def get_commit_history(
    session: Session,
    project_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[genesis_db.GitCommit]:
    """
    Return git commit history for a project (from DB — fast).

    Uses the git_commit table for O(1) queries without filesystem access.
    """
    return list(
        session.exec(
            select(genesis_db.GitCommit)
            .where(genesis_db.GitCommit.project_id == project_id)
            .order_by(sa.col(genesis_db.GitCommit.created_at).desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )


def get_diff(
    project: genesis_db.Project,
    from_commit_hash: str,
    to_commit_hash: str = "HEAD",
) -> str:
    """
    Return a unified diff between two commits.

    Args:
        project: Project with repository_path set.
        from_commit_hash: Base commit hash.
        to_commit_hash: Target commit hash (defaults to HEAD).

    Returns:
        Unified diff as a string.
    """
    repo = _get_repo(project)
    try:
        diff = repo.git.diff(from_commit_hash, to_commit_hash)
        return diff
    except GitCommandError as exc:
        raise GenesisError(
            f"Failed to generate diff: {exc!s}",
            code=ErrorCode.INTERNAL_ERROR,
        ) from exc


def restore_commit(
    session: Session,
    project: genesis_db.Project,
    commit_id: uuid.UUID,
) -> genesis_db.GitCommit:
    """
    Restore project state to a previous commit (hard reset).

    Creates a new commit on top of the restored state so history is preserved.

    Args:
        session: Database session.
        project: Target project.
        commit_id: GitCommit.id to restore to.

    Returns:
        The GitCommit record that was restored.

    Raises:
        NotFoundError: If commit not found for this project.
        GenesisError: If git operations fail.
    """
    # Verify commit belongs to this project
    commit_record = session.exec(
        select(genesis_db.GitCommit).where(
            genesis_db.GitCommit.id == commit_id,
            genesis_db.GitCommit.project_id == project.id,
        )
    ).first()

    if not commit_record:
        raise NotFoundError(
            "Commit not found for this project.",
            code=ErrorCode.NOT_FOUND,
        )

    repo = _get_repo(project)

    try:
        # Hard reset to the target commit
        repo.git.reset("--hard", commit_record.commit_hash)

        # Create a new restore commit so history is preserved
        restore_message = f"genesis(restore): restore to {commit_record.commit_hash[:8]}"
        restore_message += f"\n\nRestored-Commit: {commit_record.commit_hash}"
        restore_commit_obj = repo.index.commit(restore_message)
    except GitCommandError as exc:
        raise GenesisError(
            f"Failed to restore commit: {exc!s}",
            code=ErrorCode.INTERNAL_ERROR,
        ) from exc

    # Write new restore commit DB record
    new_commit = genesis_db.GitCommit(
        project_id=project.id,
        commit_hash=restore_commit_obj.hexsha,
        message=restore_message,
        parent_commit_hash=restore_commit_obj.parents[0].hexsha
        if restore_commit_obj.parents
        else None,
        author_type=genesis_db.GitAuthorType.SYSTEM,
        files_changed=[],
    )
    session.add(new_commit)
    project.current_commit_id = new_commit.id
    session.add(project)
    session.commit()
    session.refresh(new_commit)

    logger.info(
        "Project restored to commit",
        extra={
            "project_id": str(project.id),
            "restored_to": commit_record.commit_hash[:8],
            "new_commit": restore_commit_obj.hexsha[:8],
        },
    )
    return commit_record
