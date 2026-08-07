# ADR 0004 — API Core Technology Stack (Python / FastAPI)

| Field | Value |
|---|---|
| **Status** | Accepted |
| **Date** | 2026-08-07 |
| **Phase** | 0.3 |
| **Deciders** | Genesis Core Team |

## Context

Genesis is an AI Software Engineering OS. The core API layer will eventually need to orchestrate complex AI workflows, invoke Large Language Models (LLMs), parse Abstract Syntax Trees (ASTs), and handle vector databases.

While a Node.js API (Fastify/Express) was initially considered for web backend simplicity, the Python ecosystem is the undisputed standard for AI development (LangChain, vLLM, PyTorch, Hugging Face). Building the core in Node.js would inevitably require a complex microservice architecture to bridge to Python services. 

## Decision

**FastAPI (Python)** as the primary API framework.
**SQLModel** (SQLAlchemy + Pydantic) as the Database ORM.
**Alembic** for database migrations.
**JSON Web Tokens (JWT)** for stateless authentication.
**uv** for fast Python dependency management.

## Options Considered

### API Framework

| Option | Pros | Cons |
|---|---|---|
| **FastAPI** | Extremely fast, built on Pydantic (data validation), auto-generates OpenAPI docs, native async, pythonic | Less mature than Django/Flask |
| Fastify (Node.js) | Fast, JS/TS ecosystem | Requires bridging to Python for AI tasks later |
| Django | Batteries-included, very mature | Monolithic, heavy, async support is bolted on |
| Flask | Simple, flexible | Lacks built-in validation and async structure |

### Database ORM

| Option | Pros | Cons |
|---|---|---|
| **SQLModel** | Built by FastAPI's creator, merges Pydantic & SQLAlchemy | Newer abstraction |
| SQLAlchemy 2.0 | Extremely powerful, industry standard | Can be verbose |
| Prisma (Python) | Great DX | Python client is less standard/mature than TS version |
| Django ORM | Powerful, easy | Tied to Django |

## Rationale

### Python for AI 
Adopting Python for the API core means that in Phase 1 (AI Integration), we can import AI libraries directly into our API or worker services without cross-language serialization or sidecar containers.

### FastAPI + SQLModel
FastAPI is the modern standard for high-performance Python APIs. By combining it with SQLModel, we get a single class definition that serves as both the database schema (SQLAlchemy) and the API request/response validation model (Pydantic). This drastically reduces boilerplate.

### uv
`uv` is an extremely fast package installer and resolver written in Rust. It solves the traditional sluggishness of Python package management in a monorepo setup, making CI/CD and local development much smoother.

## Consequences

**What becomes easier:**
- AI integration in Phase 1+ will be native and seamless.
- OpenAPI docs (`/docs`) are generated automatically for free.
- Data validation is strict and automatic via Pydantic.

**What becomes harder:**
- Managing Python packages inside a JS-native Turborepo requires slight tooling adjustments (though Turborepo handles polyglot repos well).

**New constraints introduced:**
- The `@genesis/db` equivalent will be a Python package (`genesis-db`).
- All services (API, Worker) must be structured as valid Python modules.

## References
- [ADR 0003 — Tech Stack](./0003-tech-stack.md)
