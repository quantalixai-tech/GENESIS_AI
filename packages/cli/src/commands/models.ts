/**
 * genesis models
 *
 * Manage AI models for the platform.
 *
 * Sub-commands (Phase 1.0+):
 *   genesis models list        — List available and downloaded models
 *   genesis models pull <name> — Download a model (via Ollama)
 *   genesis models remove <name> — Remove a downloaded model
 *   genesis models inspect <name> — Show model details
 *   genesis models default <name> — Set the default model
 *
 * This command is a Phase 1.0 concern — AI services are not yet active.
 * The stub is defined here to reserve the command name and document intent.
 */

// TODO(phase-1.0): Implement models command
export const modelsCommand = {
  name: 'models',
  description: 'Manage AI models',
  handler: async () => {
    throw new Error('Not implemented — Phase 1.0');
  },
};
