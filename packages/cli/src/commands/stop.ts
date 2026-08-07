/**
 * genesis stop
 *
 * Stop all platform services (preserves data).
 *
 * Responsibilities (Phase 0.3+):
 *   - Execute docker compose down
 *   - Confirm services are stopped
 *   - Print status
 *
 * For destructive cleanup (remove volumes), use: genesis clean
 *
 * Today this delegates to scripts/down.sh.
 */

// TODO(phase-0.3): Implement stop command
export const stopCommand = {
  name: 'stop',
  description: 'Stop all platform services (data is preserved)',
  handler: async () => {
    throw new Error('Not implemented — Phase 0.3');
  },
};
