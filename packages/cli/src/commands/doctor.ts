/**
 * genesis doctor
 *
 * Run health checks across the entire platform.
 *
 * See: docs/rfc/0004-health.md for the full health specification.
 *
 * Checks (Phase 0.3+):
 *   ✓ Docker — is Docker installed and running?
 *   ✓ PostgreSQL — is the database reachable and healthy?
 *   ✓ NATS — is the event bus reachable and healthy?
 *   ✓ MinIO — is object storage reachable and healthy?
 *   ✓ Disk — is there sufficient disk space?
 *   ✓ Ports — are required ports available?
 *   ✓ GPU — is a GPU available for AI workloads? (optional)
 *   ✓ Models — are required AI models downloaded? (optional)
 *
 * Output format:
 *   ✓ Docker          — running (version 27.x)
 *   ✓ PostgreSQL      — healthy (localhost:5432)
 *   ✓ NATS            — healthy (localhost:4222)
 *   ✓ MinIO           — healthy (localhost:9000)
 *   ✓ Disk            — 120 GB available
 *   ✓ Ports           — all required ports available
 *   ○ GPU             — not available (CPU mode)
 *   ○ Models          — not configured
 *
 * Exit codes:
 *   0 — all required checks pass
 *   1 — one or more required checks failed
 */

// TODO(phase-0.3): Implement doctor command
export const doctorCommand = {
  name: 'doctor',
  description: 'Run platform health checks',
  handler: async () => {
    throw new Error('Not implemented — Phase 0.3');
  },
};
