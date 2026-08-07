# =============================================================================
# Genesis API — Dockerfile
# Uses uv for fast, reproducible dependency installation.
# The single .venv is built from the monorepo root uv.lock.
# =============================================================================

FROM python:3.11-slim AS builder

# Install build deps (needed for psycopg2-binary compile on some platforms)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv from the official image
COPY --from=ghcr.io/astral-sh/uv:0.12.2 /uv /bin/uv

WORKDIR /app

# ── 1. Copy only the files uv needs to resolve & install dependencies ──────
COPY pyproject.toml uv.lock ./
COPY packages/db/pyproject.toml packages/db/pyproject.toml
COPY apps/api/pyproject.toml apps/api/pyproject.toml

# ── 2. Copy source that needs to be built (genesis_db is a local package) ──
COPY packages/db/genesis_db packages/db/genesis_db

# ── 3. Install all dependencies into a single .venv ──────────────────────
#    --no-install-project: skip installing 'api' itself (it's not a lib)
#    --package api: install deps declared by the 'api' workspace member
RUN uv sync --package api --no-install-project --frozen

# =============================================================================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy the pre-built venv from builder
COPY --from=builder /app/.venv /app/.venv

# Copy actual application source
COPY packages/db/genesis_db packages/db/genesis_db
COPY apps/api/src apps/api/src

# Set PATH so .venv binaries are used, set PYTHONPATH for module resolution
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/api/src:/app/packages/db"
ENV PORT=8080

EXPOSE 8080

# Run from repo root; uvicorn finds 'main:app' via PYTHONPATH
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
