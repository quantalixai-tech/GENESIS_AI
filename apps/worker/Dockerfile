# =============================================================================
# Genesis Worker — Dockerfile
# Uses uv for fast, reproducible dependency installation.
# =============================================================================

FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:0.12.2 /uv /bin/uv

WORKDIR /app

# ── 1. Copy only files uv needs ────────────────────────────────────────────
COPY pyproject.toml uv.lock ./
COPY packages/db/pyproject.toml packages/db/pyproject.toml
COPY apps/worker/pyproject.toml apps/worker/pyproject.toml

# ── 2. Copy local package source ───────────────────────────────────────────
COPY packages/db/genesis_db packages/db/genesis_db

# ── 3. Install all worker dependencies into a single .venv ─────────────────
RUN uv sync --package worker --no-install-project --frozen

# =============================================================================
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /app/.venv /app/.venv
COPY packages/db/genesis_db packages/db/genesis_db
COPY apps/worker/src apps/worker/src

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/apps/worker/src:/app/packages/db"

CMD ["python", "apps/worker/src/main.py"]
