/**
 * genesis start
 *
 * Start all platform services.
 *
 * Responsibilities (Phase 0.3+):
 *   - Run pre-flight checks (Docker running, .env exists)
 *   - Execute docker compose up -d
 *   - Wait for health checks to pass
 *   - Print service endpoints
 *   - Open dashboard in browser (optional)
 *
 * Today this delegates to scripts/up.sh.
 * In Phase 0.3, this becomes a proper CLI command.
 */

// TODO(phase-0.3): Implement start command
export const startCommand = {
  name: 'start',
  description: 'Start all platform services',
  handler: async () => {
    throw new Error('Not implemented — Phase 0.3');
  },
};
