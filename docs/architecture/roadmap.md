# GENESIS AI — Development Roadmap

This document outlines the strategic phases for developing GENESIS AI, detailing what has been accomplished and the path forward.

## Phase 0.5: Developer Experience & Tooling (Completed)
**Goal:** Establish a robust, reproducible, and fast local development environment.
- **DevContainer Architecture:** Fully containerized, process-based local development.
- **`genesis` CLI:** Unified command-line interface for managing setup, services, databases, and logs without relying on brittle shell scripts.
- **Monorepo Setup:** Turborepo configuring Next.js frontend, FastAPI backend, and shared UI/DB packages.
- **Hot-Reloading:** Native hot-reloading for both backend (`uvicorn`) and frontend (`pnpm dev`) within the IDE container.

## Phase 1.0: Core Infrastructure & Deployment (Current)
**Goal:** Finalize the base application infrastructure, database schema, and production deployment mechanisms.
- **Production Docker Images:** Establish clean, optimized, and separate Dockerfiles for API and Web utilizing a multi-stage Turborepo prune strategy.
- **Database Schema:** Finalize the SQLAlchemy / SQLModel definitions in `genesis_db`.
- **Alembic Migrations:** Solidify the migration pipeline via `genesis migrate`.
- **Core Services Integration:** Ensure Postgres, MinIO (S3), and NATS are fully integrated and accessible to the platform components.
- **Frontend Foundations:** Tailwind CSS v4, CSS Modules integration, and core UI components.

## Phase 2.0: AI Agent Workflows & Orchestration (Next)
**Goal:** Introduce the core value proposition of GENESIS AI—autonomous AI agents and workflow execution.
- **Agent Registry:** Implement dynamic model and agent registration in the database (`model_registry`, `agent_registry`).
- **Prompt Management:** System prompt registry to prevent inline prompt injections and allow versioning.
- **NATS Worker Queue:** Implement robust message consumption in the `worker` app to execute long-running AI tasks asynchronously.
- **AI Run Tracking:** Create and monitor `ai_run` records for tracking executions, maintaining safety, and collecting evaluations.
- **Governance & Approvals:** Implement risk-level evaluation and explicit user-approval gates for HIGH/CRITICAL actions.

## Phase 3.0: UI Polish, Dashboards & Scalability (Future)
**Goal:** Deliver a premium user experience and prepare the system for horizontal scaling.
- **Web Dashboards:** Comprehensive UI for managing agents, viewing run histories, and system health.
- **Premium Design:** Iterative UI improvements leveraging Tailwind CSS, Micro-animations, and dynamic data presentation.
- **Telemetry & Monitoring:** Add robust tracing, logging aggregation, and alerting metrics.
- **Production Readiness:** Kubernetes helm charts or equivalent cloud-native deployment configurations.
