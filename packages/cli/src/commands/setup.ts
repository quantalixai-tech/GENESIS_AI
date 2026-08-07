/**
 * genesis setup
 *
 * First-time environment setup.
 *
 * Responsibilities (Phase 0.3+):
 *   - Check Docker is installed and running
 *   - Create .env from .env.example if not present
 *   - Validate infrastructure compose file
 *   - Initialize default configuration
 *   - Print next steps
 *
 * Today this delegates to scripts/setup.sh.
 * In Phase 0.3, this becomes a proper CLI command with rich output.
 */

// TODO(phase-0.3): Implement setup command
export const setupCommand = {
  name: 'setup',
  description: 'First-time environment setup',
  handler: async () => {
    throw new Error('Not implemented — Phase 0.3');
  },
};
