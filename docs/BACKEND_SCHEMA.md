# BACKEND_SCHEMA

**Document ID:** DB-001  
**Project:** AI-Driven Software Development Platform  
**Version:** 0.1.0  
**Status:** Draft

---

# 1. Purpose

This document defines the initial backend data model for the AI-driven software development platform.

The schema is designed around:

- Users
- Projects
- Conversations
- Requirements
- Features
- Use cases
- Application flows
- UI/UX artifacts
- Technical requirements
- Implementation plans
- Tasks
- Project files
- Project index
- AI agents
- Agent executions
- Validation runs
- Errors
- Repairs
- Git history
- Environments
- Feedback

---

# 2. Data Model Overview

```text
User
 |
 +---- Projects
        |
        +---- Conversations
        |
        +---- Requirements
        |
        +---- Features
        |
        +---- Use Cases
        |
        +---- Screens
        |
        +---- Technical Requirements
        |
        +---- Implementation Plans
        |
        +---- Tasks
        |
        +---- Files
        |
        +---- Project Index
        |
        +---- Agent Runs
        |
        +---- Validation Runs
        |
        +---- Errors
        |
        +---- Repairs
        |
        +---- Git Commits
        |
        +---- Feedback
        |
        +---- Environments
```

---

# 3. Core Entities

## 3.1 users

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR | NOT NULL |
| email | VARCHAR | UNIQUE |
| role | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 4. projects

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| owner_id | UUID | FK users.id |
| name | VARCHAR | NOT NULL |
| description | TEXT | NULL |
| project_type | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| repository_path | TEXT | NULL |
| current_commit_id | UUID | NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

Possible status values:

```text
DISCOVERY
PLANNING
IMPLEMENTING
VALIDATING
READY
BLOCKED
ARCHIVED
```

---

# 5. conversations

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| status | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 6. conversation_messages

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| conversation_id | UUID | FK conversations.id |
| role | VARCHAR | NOT NULL |
| content | TEXT | NOT NULL |
| message_type | VARCHAR | NOT NULL |
| metadata | JSONB | NULL |
| created_at | TIMESTAMP | NOT NULL |

Roles:

```text
USER
ASSISTANT
SYSTEM
AGENT
```

---

# 7. requirements

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| requirement_key | VARCHAR | UNIQUE PER PROJECT |
| title | VARCHAR | NOT NULL |
| description | TEXT | NOT NULL |
| category | VARCHAR | NOT NULL |
| priority | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| confidence | DECIMAL | NULL |
| source_message_id | UUID | NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

Categories:

```text
FUNCTIONAL
NON_FUNCTIONAL
SECURITY
PERFORMANCE
UX
TECHNICAL
CONSTRAINT
```

---

# 8. features

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| feature_key | VARCHAR | UNIQUE PER PROJECT |
| name | VARCHAR | NOT NULL |
| description | TEXT | NULL |
| status | VARCHAR | NOT NULL |
| priority | VARCHAR | NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 9. use_cases

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| use_case_key | VARCHAR | UNIQUE PER PROJECT |
| name | VARCHAR | NOT NULL |
| actor | VARCHAR | NOT NULL |
| description | TEXT | NOT NULL |
| preconditions | JSONB | NULL |
| postconditions | JSONB | NULL |
| status | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 10. screens

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| screen_key | VARCHAR | UNIQUE PER PROJECT |
| name | VARCHAR | NOT NULL |
| route | VARCHAR | NULL |
| description | TEXT | NULL |
| ui_spec | JSONB | NULL |
| status | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 11. technical_requirements

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| requirement_key | VARCHAR | UNIQUE PER PROJECT |
| title | VARCHAR | NOT NULL |
| description | TEXT | NOT NULL |
| category | VARCHAR | NOT NULL |
| priority | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 12. implementation_plans

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| version | INTEGER | NOT NULL |
| status | VARCHAR | NOT NULL |
| plan_data | JSONB | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

---

# 13. implementation_tasks

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| task_key | VARCHAR | UNIQUE PER PROJECT |
| title | VARCHAR | NOT NULL |
| description | TEXT | NOT NULL |
| task_type | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| priority | VARCHAR | NULL |
| agent_type | VARCHAR | NULL |
| parallelizable | BOOLEAN | DEFAULT FALSE |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 14. task_dependencies

| Field | Type | Constraints |
|---|---|---|
| task_id | UUID | FK implementation_tasks.id |
| depends_on_task_id | UUID | FK implementation_tasks.id |
| dependency_type | VARCHAR | NOT NULL |

Primary key:

```text
(task_id, depends_on_task_id)
```

---

# 15. project_files

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| path | TEXT | NOT NULL |
| file_type | VARCHAR | NULL |
| language | VARCHAR | NULL |
| content_hash | VARCHAR | NOT NULL |
| size_bytes | BIGINT | NULL |
| status | VARCHAR | NOT NULL |
| last_indexed_at | TIMESTAMP | NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

---

# 16. project_index

The project index represents relationships between project artifacts.

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| file_id | UUID | FK project_files.id |
| symbol_name | VARCHAR | NULL |
| symbol_type | VARCHAR | NULL |
| route | VARCHAR | NULL |
| api_reference | VARCHAR | NULL |
| entity_reference | VARCHAR | NULL |
| requirement_ids | JSONB | NULL |
| dependency_ids | JSONB | NULL |
| test_ids | JSONB | NULL |
| metadata | JSONB | NULL |
| content_hash | VARCHAR | NOT NULL |
| indexed_at | TIMESTAMP | NOT NULL |

---

# 17. index_relationships

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| source_type | VARCHAR | NOT NULL |
| source_id | UUID | NOT NULL |
| target_type | VARCHAR | NOT NULL |
| target_id | UUID | NOT NULL |
| relationship_type | VARCHAR | NOT NULL |
| metadata | JSONB | NULL |

Example relationships:

```text
REQUIREMENT -> FEATURE
FEATURE -> USE_CASE
USE_CASE -> SCREEN
SCREEN -> COMPONENT
COMPONENT -> FILE
FILE -> API
API -> ENTITY
FILE -> TEST
TASK -> FILE
TASK -> REQUIREMENT
```

---

# 18. agents

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| name | VARCHAR | UNIQUE |
| agent_type | VARCHAR | NOT NULL |
| description | TEXT | NULL |
| configuration | JSONB | NULL |
| enabled | BOOLEAN | DEFAULT TRUE |
| created_at | TIMESTAMP | NOT NULL |

Possible agent types:

```text
REQUIREMENT
PRODUCT
UI
ARCHITECTURE
FRONTEND
BACKEND
DATABASE
PLANNER
CODER
TEST
BUILD
DEBUG
REPAIR
DOCUMENTATION
INDEX
REVIEW
ORCHESTRATOR
```

---

# 19. agent_runs

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| agent_id | UUID | FK agents.id |
| task_id | UUID | NULL |
| status | VARCHAR | NOT NULL |
| input_context | JSONB | NULL |
| output_summary | JSONB | NULL |
| started_at | TIMESTAMP | NULL |
| completed_at | TIMESTAMP | NULL |
| error_id | UUID | NULL |

---

# 20. validation_runs

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| commit_id | UUID | NULL |
| validation_type | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| output | TEXT | NULL |
| duration_ms | BIGINT | NULL |
| started_at | TIMESTAMP | NOT NULL |
| completed_at | TIMESTAMP | NULL |

Validation types:

```text
SYNTAX
TYPECHECK
LINT
UNIT
INTEGRATION
E2E
BUILD
RUNTIME
SECURITY
UI
```

---

# 21. errors

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| validation_run_id | UUID | NULL |
| error_type | VARCHAR | NOT NULL |
| error_code | VARCHAR | NULL |
| message | TEXT | NOT NULL |
| stack_trace | TEXT | NULL |
| affected_files | JSONB | NULL |
| severity | VARCHAR | NOT NULL |
| status | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |

---

# 22. repairs

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| error_id | UUID | FK errors.id |
| agent_run_id | UUID | NULL |
| diagnosis | TEXT | NULL |
| repair_plan | JSONB | NULL |
| changed_files | JSONB | NULL |
| status | VARCHAR | NOT NULL |
| attempt_number | INTEGER | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| completed_at | TIMESTAMP | NULL |

---

# 23. git_commits

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| commit_hash | VARCHAR | NOT NULL |
| message | TEXT | NOT NULL |
| parent_commit_hash | VARCHAR | NULL |
| author_type | VARCHAR | NOT NULL |
| task_id | UUID | NULL |
| created_at | TIMESTAMP | NOT NULL |

Author types:

```text
USER
AI
SYSTEM
```

---

# 24. environments

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| name | VARCHAR | NOT NULL |
| environment_type | VARCHAR | NOT NULL |
| configuration | JSONB | NULL |
| status | VARCHAR | NOT NULL |
| created_at | TIMESTAMP | NOT NULL |
| updated_at | TIMESTAMP | NOT NULL |

Environment types:

```text
LOCAL
TEST
STAGING
PRODUCTION
```

---

# 25. feedback

| Field | Type | Constraints |
|---|---|---|
| id | UUID | PK |
| project_id | UUID | FK projects.id |
| user_id | UUID | FK users.id |
| message | TEXT | NOT NULL |
| feedback_type | VARCHAR | NULL |
| status | VARCHAR | NOT NULL |
| impact_analysis | JSONB | NULL |
| created_at | TIMESTAMP | NOT NULL |

---

# 26. Requirement Relationships

Requirements may connect to:

```text
Requirement
    |
    +---- Feature
    |
    +---- Use Case
    |
    +---- Screen
    |
    +---- Technical Requirement
    |
    +---- Task
    |
    +---- File
    |
    +---- Test
```

---

# 27. Database Indexing Strategy

Indexes should be created for frequent access paths.

Expected indexes include:

```text
projects.owner_id
requirements.project_id
features.project_id
use_cases.project_id
screens.project_id
implementation_tasks.project_id
implementation_tasks.status
project_files.project_id
project_files.path
project_index.project_id
project_index.file_id
agent_runs.project_id
validation_runs.project_id
errors.project_id
git_commits.project_id
feedback.project_id
```

---

# 28. Data Integrity

The database must enforce:

- Foreign key relationships
- Required fields
- Unique project keys
- Referential integrity
- Valid status values where practical
- Transaction boundaries for critical operations

---

# 29. Audit Requirements

Important project changes should be traceable to:

- User
- AI agent
- Task
- Commit
- Requirement
- Validation

---

# 30. Future Schema Extensions

Potential future entities:

- Organizations
- Teams
- Project members
- Deployments
- Secrets
- Model configurations
- Agent policies
- Tool permissions
- Plugins
- Usage records
- Billing
- Collaboration sessions

---

# END OF BACKEND SCHEMA
