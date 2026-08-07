/**
 * genesis plugins
 *
 * Manage Genesis plugins (extensions to the platform).
 *
 * Sub-commands (Phase 2.0+):
 *   genesis plugins list           — List installed plugins
 *   genesis plugins install <name> — Install a plugin
 *   genesis plugins remove <name>  — Remove a plugin
 *   genesis plugins enable <name>  — Enable a plugin
 *   genesis plugins disable <name> — Disable a plugin
 *   genesis plugins inspect <name> — Show plugin details
 *
 * The plugin system is a Phase 2.0 concern.
 * This stub reserves the command name and documents intent.
 */

// TODO(phase-2.0): Implement plugins command
export const pluginsCommand = {
  name: 'plugins',
  description: 'Manage platform plugins',
  handler: async () => {
    throw new Error('Not implemented — Phase 2.0');
  },
};
