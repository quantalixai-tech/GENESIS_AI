# AI_GOVERNANCE

**Document ID:** GOV-001
**Project:** GENESIS AI — AI-Driven Software Development Platform
**Version:** 0.1.0
**Status:** Active
**Last Updated:** 2026-08-08

> This document defines the governance framework for all AI models, prompts, agents, tools, and executions within the GENESIS AI platform. It is an engineering document, not a policy aspiration — compliance is enforced structurally through code and database schema.

---

# 1. Governance Philosophy

GENESIS AI generates software using AI agents. Every AI-driven action therefore has real consequences:
files are written, databases are migrated, external services are called, user code is modified.

The governance framework exists to ensure that:

1. **Every AI action is traceable** — to a user, a request, an agent, a model, and a prompt version.
2. **Models and prompts are versioned** — changes to AI behavior are deliberate and trackable.
3. **Agents have defined boundaries** — no agent has unrestricted access to tools or infrastructure.
4. **High-risk actions require approval** — irreversible or destructive AI actions require human sign-off.
5. **AI output is treated as untrusted** — LLM output is validated before being acted upon.
6. **Governance is structural** — these constraints are enforced by database schema and middleware, not documentation only.

---

# 2. Model Governance

## 2.1 Model Registry

All LLM models must be registered in the `model_registry` database table before use.

**Forbidden:**
```python
# BAD — hardcoded model name, no audit trail
client.chat.completions.create(model="gpt-4o", ...)
```

**Required:**
```python
# GOOD — model referenced by registry ID
model = session.get(ModelRegistry, agent.model_id)
client.chat.completions.create(model=model.model_id, ...)
```

## 2.2 Model Registration Fields

| Field | Required | Purpose |
|---|---|---|
| `name` | Yes | Human-readable name |
| `model_id` | Yes | Provider API identifier |
| `provider` | Yes | openai / anthropic / google / ollama / custom |
| `version` | Yes | Model snapshot or version string |
| `context_window` | Recommended | For context management |
| `capabilities` | Recommended | vision, function_calling, json_mode |

## 2.3 Model Change Policy

- When a model is updated or replaced, create a new registry entry.
- Update agent registry entries to reference the new model.
- Do not delete old registry entries — they are audit records.
- Document the reason for model change in the model registry entry description.

---

# 3. Prompt Governance

## 3.1 Prompt Registry

All system prompts used by agents must be registered in the `prompt_registry` table.

**Forbidden:**
```python
# BAD — anonymous inline prompt, no versioning, no audit trail
messages = [{"role": "system", "content": "You are a helpful assistant that..."}]
```

**Required:**
```python
# GOOD — prompt referenced by registry ID
prompt = session.get(PromptRegistry, agent.system_prompt_id)
messages = [{"role": "system", "content": prompt.content}]
```

## 3.2 Prompt Versioning

- Every update to a prompt is a new registry record with an incremented `version`.
- Old prompt records are set to `status=DEPRECATED`, never deleted.
- AI runs reference the exact `prompt_registry.id` used — enabling post-hoc analysis.

## 3.3 Prompt Fields

| Field | Required | Purpose |
|---|---|---|
| `prompt_key` | Yes | Stable identifier (e.g., `requirement_agent_system`) |
| `version` | Yes | Monotonically increasing integer |
| `title` | Yes | Human-readable title |
| `content` | Yes | Full prompt text |
| `status` | Yes | draft / active / deprecated / archived |
| `owner` | Recommended | Team or service responsible |
| `evaluation_status` | Recommended | passed / failed / pending |

## 3.4 Prompt Security

- Never include user-provided content directly in system prompts without sanitization.
- Validate that prompt content does not contain injection-susceptible patterns.
- Do not include API keys, credentials, or internal URLs in prompt registry entries.

---

# 4. Agent Governance

## 4.1 Agent Registry

All agents must be registered in the `agent_registry` table before they can be instantiated by the orchestrator. Unregistered agents cannot be invoked.

## 4.2 Agent Fields

| Field | Required | Purpose |
|---|---|---|
| `agent_key` | Yes | Stable unique identifier |
| `name` | Yes | Human-readable name |
| `agent_type` | Yes | Classification (REQUIREMENT / CODER / REPAIR / etc.) |
| `purpose` | Yes | What this agent does |
| `allowed_tools` | Yes | Explicit whitelist of tool IDs |
| `risk_level` | Yes | low / medium / high / critical |
| `requires_approval` | Yes | Whether actions need human sign-off |
| `max_execution_seconds` | Yes | Hard timeout |
| `max_retries` | Yes | Retry limit |

## 4.3 Risk Levels and Approval Requirements

| Risk Level | Description | Approval Required |
|---|---|---|
| `low` | Read-only, fully reversible | No |
| `medium` | Writes data, reversible | No — but audit logged |
| `high` | Irreversible or external action | Async human approval |
| `critical` | Production changes, bulk destruction | Synchronous human-in-the-loop |

## 4.4 Agent Capability Rules

- Agents may ONLY use tools explicitly listed in `allowed_tools`.
- Agents may not add tools to their own allowed list at runtime.
- Agents may not spawn sub-agents with higher risk levels than themselves.
- Agents with `risk_level=high` or `critical` must have `requires_approval=true`.

---

# 5. Tool Governance

## 5.1 Tool Classification

Tools are classified by their side-effect profile:

| Class | Examples | Default Risk |
|---|---|---|
| `READ` | Read file, query DB, search index | Low |
| `WRITE` | Write file, create record, update state | Medium |
| `DELETE` | Remove file, delete record | High |
| `EXECUTE` | Run command, trigger build, run tests | High |
| `EXTERNAL_ACTION` | Send email, call external API, deploy | Critical |

## 5.2 Tool Requirements

Every tool must define:

- **Tool ID** — stable string identifier
- **Description** — what the tool does
- **Input schema** — Pydantic model for input validation
- **Output schema** — Pydantic model for output validation
- **Risk class** — READ / WRITE / DELETE / EXECUTE / EXTERNAL_ACTION
- **Side effects** — what the tool changes
- **Reversible** — whether the action can be undone
- **Timeout** — maximum execution time
- **Audit required** — whether every invocation is logged

## 5.3 Tool Output Validation

**LLM output is untrusted.** When an agent invokes a tool using LLM-generated arguments:

1. Arguments MUST be validated against the tool's input schema before execution.
2. If validation fails, the tool call is rejected — not retried with the raw output.
3. Output from external tools is validated against the output schema before use in business logic.
4. Never use raw string output from an LLM to construct file paths, SQL queries, or shell commands.

---

# 6. Human-in-the-Loop

## 6.1 When Approval Is Required

The following actions require explicit human approval before execution:

- Deleting any project data (files, database records)
- Sending external communications (email, webhooks)
- Modifying production environments
- Bulk file modifications (more than N files in a single operation)
- Database schema modifications on populated databases
- Any action classified as `critical` risk level

## 6.2 Approval Mechanism

1. Agent creates an `ai_run` record with `status=APPROVAL_REQUIRED` and `approval_state=pending`.
2. The platform notifies the user via the conversation interface.
3. User reviews the proposed action and either approves or rejects.
4. On approval: `ai_run.approval_state=approved`, execution proceeds.
5. On rejection: `ai_run.approval_state=rejected`, action is cancelled and user is informed.
6. Approvals have a timeout — if not responded to within X minutes, the action is auto-cancelled.

## 6.3 Approval Cannot Be Bypassed

- No code path may execute a high/critical risk action without checking `ai_run.approval_state`.
- This check is enforced in the service layer, not in agent code (agents cannot bypass it).

---

# 7. AI Execution Records (AIRun)

## 7.1 Mandatory Record Creation

Every AI operation MUST create an `ai_run` record. This is non-negotiable.

Services that invoke AI agents are responsible for creating and updating the `ai_run` record. Agents themselves do not manage their own records.

## 7.2 Required Fields

Every `ai_run` must capture:

| Field | Requirement |
|---|---|
| `run_type` | Always |
| `status` | Always (updated throughout lifecycle) |
| `agent_id` | When an agent is involved |
| `model_id` | When an LLM is called |
| `prompt_id` | When a registered prompt is used |
| `triggered_by_user_id` | When triggered by user action |
| `project_id` | When associated with a project |

## 7.3 What NOT to Store

The following MUST NOT be stored in `ai_run`:

- Full LLM prompt content (reference `prompt_registry.id`)
- Raw user messages (reference conversation records)
- API keys or credentials
- Passwords or sensitive user data
- Full stack traces (sanitize before storing in `error_message`)

## 7.4 Observability Fields

Capture when available:
- `duration_ms` — total execution time
- `prompt_tokens`, `completion_tokens`, `total_tokens` — for cost tracking
- `estimated_cost_usd` — calculated from token counts and model pricing
- `tools_used` — list of tool IDs called

---

# 8. AI Security

## 8.1 Prompt Injection

- Never interpolate raw user input directly into system prompts.
- Treat all user-provided content as potentially malicious.
- Use structured input formats (JSON, typed schemas) rather than free text when passing user data to agents.
- Log and alert on prompt content that attempts to override system instructions.

## 8.2 Indirect Prompt Injection

- Content retrieved from external sources (web pages, user-uploaded files, databases) may contain adversarial instructions.
- This content must be explicitly marked as "external data" in the agent context, not as instructions.
- Agents must be instructed to treat external content as data, not commands.

## 8.3 Excessive Agency

- Agents must not be given more permissions than their current task requires.
- The orchestrator must pass only the tools and context needed for the specific task.
- Agents must not retain state between executions that could escalate their effective permissions.

## 8.4 Output Validation

- All LLM-generated structured output (JSON, code, schemas) must be validated before use.
- Validation failures must not be silently retried — they must be logged and escalated.
- Generated code must not be executed without a validation pass (syntax check, type check, security scan).

## 8.5 Cross-User Data Protection

- Each AI run must be scoped to a specific user and project.
- AI context must never include data from other users' projects.
- The orchestrator must verify project ownership before injecting project context.

---

# 9. Evaluation

## 9.1 AI Evaluation Requirements

Before deploying or updating any agent or prompt:

1. **Correctness** — Does the agent produce the expected output for representative inputs?
2. **Tool selection** — Does the agent choose the appropriate tools?
3. **Structured output** — Does the agent produce valid, schema-conformant structured output?
4. **Safety** — Does the agent refuse or escalate appropriately on adversarial inputs?
5. **Prompt regression** — Does a prompt update maintain or improve baseline performance?
6. **Failure handling** — Does the agent fail gracefully and not corrupt state?

## 9.2 Evaluation Records

Evaluation results are stored in `prompt_registry.evaluation_status` for prompts and in dedicated evaluation records (future: `evaluation_registry` table).

---

# 10. Logging Requirements

## 10.1 Required Log Events

Every service must log:

- Agent invocation start (agent_id, run_type, project_id, user_id)
- Agent invocation end (status, duration_ms, token counts)
- Tool calls (tool_id, input summary, output summary, duration)
- Policy decisions (allow / deny / approval_required)
- Validation failures (what failed, why)
- Human approval events (approved / rejected, by whom)

## 10.2 Forbidden Log Content

Never log:
- Passwords or hashed passwords
- JWT tokens or API keys
- Full LLM prompt content (log prompt_registry.id instead)
- Full LLM completion content containing user PII
- Database connection strings
- Internal IP addresses or hostnames (in user-facing logs)

---

# 11. Development Rules for AI Features

When building any AI-powered feature:

1. **Register before building** — register the model, prompt, and agent in the database before writing agent code.
2. **Define tool boundaries** — explicitly list every tool the agent needs; request no more.
3. **Write evaluation cases** — define expected behavior before implementation.
4. **Validate all inputs** — never pass raw LLM output to tools or DB without schema validation.
5. **Create AIRun records** — every AI execution path must create an `ai_run` record.
6. **Test failure paths** — what happens when the LLM returns malformed output? When a tool fails? When the user rejects approval?
7. **Update this document** — when a new agent or tool is introduced, update the relevant registry and this document.

---

# 12. Governance Checklist (Pre-Merge)

Before merging any AI feature:

- [ ] Model registered in `model_registry`
- [ ] Prompt registered in `prompt_registry` (no inline system prompts)
- [ ] Agent registered in `agent_registry` with explicit `allowed_tools`
- [ ] Risk level assigned and documented
- [ ] `ai_run` records created in all execution paths
- [ ] LLM output validated against schema before use
- [ ] No user PII in log statements
- [ ] Evaluation cases written and passing
- [ ] Failure paths tested
- [ ] Documentation updated

---

# END OF AI GOVERNANCE DOCUMENT
