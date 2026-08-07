# Phase 0.2 — Infrastructure Bootstrap Tasks

## Environment Files
- [x] `.env.example`
- [x] `.env.development`
- [x] `.env` (gitignored, seeded from .env.example)

## Infrastructure — Docker Compose
- [x] `infrastructure/docker/compose/docker-compose.yml`
- [x] `infrastructure/docker/compose/docker-compose.override.yml`
- [x] `infrastructure/docker/images/.gitkeep`
- [x] `infrastructure/docker/volumes/.gitkeep`

## Service Configs
- [x] `infrastructure/postgres/init.sql`
- [x] `infrastructure/nats/nats.conf`
- [x] `infrastructure/minio/.gitkeep`
- [x] `infrastructure/version.json`

## Shell Scripts
- [x] `scripts/setup.sh`
- [x] `scripts/up.sh`
- [x] `scripts/down.sh`
- [x] `scripts/restart.sh`
- [x] `scripts/clean.sh`

## CLI Package Scaffold
- [x] `packages/cli/package.json`
- [x] `packages/cli/tsconfig.json`
- [x] `packages/cli/src/index.ts`
- [x] `packages/cli/src/commands/setup.ts`
- [x] `packages/cli/src/commands/start.ts`
- [x] `packages/cli/src/commands/stop.ts`
- [x] `packages/cli/src/commands/doctor.ts`
- [x] `packages/cli/src/commands/config.ts`
- [x] `packages/cli/src/commands/models.ts`
- [x] `packages/cli/src/commands/plugins.ts`
- [x] `packages/cli/src/commands/workspace.ts`
- [x] `packages/cli/src/config/index.ts`
- [x] `packages/cli/src/utils/index.ts`
- [x] `packages/cli/src/types/index.ts`

## Apps
- [x] `apps/dashboard/.gitkeep`

## Documentation
- [x] `docs/infrastructure.md`
- [x] `docs/rfc/0004-health.md`
- [x] `docs/process.md` (ADR→RFC→Impl→AC→Verify pattern)

## Root package.json
- [x] Add infra convenience scripts

## Verification
- [ ] `docker compose up -d` — all three services healthy
- [ ] Scripts are executable and work correctly
