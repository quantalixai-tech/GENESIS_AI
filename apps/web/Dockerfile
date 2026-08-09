# =============================================================================
# Genesis Web — Dockerfile
#
# Multi-stage build using Turborepo's Docker pruning strategy.
# Produces a minimal standalone Next.js image.
#
# Image name: genesis-web:local
# =============================================================================

# Stage 1: Prune the monorepo to only the files needed for 'web'
FROM node:22-alpine AS pruner
# libc6-compat required for Alpine + native binaries
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install turbo globally for the prune step
RUN npm install -g turbo@^2 pnpm@9 --silent

COPY . .
# Prune the monorepo to only what 'web' needs, outputting two directories:
#   out/json/  — package.json files and lockfile only (for dep install layer cache)
#   out/full/  — full source code for the packages web depends on
RUN turbo prune web --docker

# =============================================================================
# Stage 2: Install dependencies from the pruned lockfile
# =============================================================================
FROM node:22-alpine AS installer
RUN apk add --no-cache libc6-compat
WORKDIR /app

RUN npm install -g pnpm@9 --silent

# First, restore the pruned package manifests + lockfile
# This layer is cached unless package deps change
COPY --from=pruner /app/out/json/ .
COPY --from=pruner /app/out/pnpm-lock.yaml ./pnpm-lock.yaml
RUN pnpm install --frozen-lockfile

# Copy the pruned source code (after deps so source changes don't bust dep cache)
COPY --from=pruner /app/out/full/ .
# turbo.json is needed at the workspace root for `turbo run build`
COPY --from=pruner /app/turbo.json turbo.json

# Disable Next.js telemetry during build
ENV NEXT_TELEMETRY_DISABLED=1

# Build the Next.js application
RUN pnpm turbo run build --filter=web...

# =============================================================================
# Stage 3: Minimal production runner
# =============================================================================
FROM node:22-alpine AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

# Create a non-root user for security
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Create the .next directory with correct ownership before copying
RUN mkdir -p /app/.next
RUN chown -R nextjs:nodejs /app

# Next.js standalone output creates a self-contained server.js at the root
# of the standalone directory. Copy it along with static assets and public files.
COPY --from=installer --chown=nextjs:nodejs /app/apps/web/.next/standalone ./
COPY --from=installer --chown=nextjs:nodejs /app/apps/web/.next/static ./apps/web/.next/static
COPY --from=installer --chown=nextjs:nodejs /app/apps/web/public ./apps/web/public

USER nextjs

EXPOSE 3000

# The standalone output places server.js at apps/web/server.js relative to the
# output root (which is now our WORKDIR).
CMD ["node", "apps/web/server.js"]
